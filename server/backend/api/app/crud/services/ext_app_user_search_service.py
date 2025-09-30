import logging
from http import HTTPStatus
from typing import List

from api.app.constants import (ERROR_CODE_INVALID_OPERATION, EXT_MIN_PAGE,
                               EXT_MIN_PAGE_SIZE, IDPType, ScopeType, UserType)
from api.app.models.model import FamRole, FamUser, FamUserRoleXref
from api.app.schemas.ext.pagination import (ExtUserSearchPagedResultsSchema,
                                            ExtUserSearchParamSchema)
from api.app.schemas.ext.user_search import (ExtApplicationUserSearchGetSchema,
                                             ExtApplicationUserSearchSchema,
                                             ExtRoleWithScopeSchema)
from api.app.schemas.requester import RequesterSchema
from api.app.utils.utils import raise_http_exception
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.selectable import Select

from .ext_api_interface import ExtAPIInterface

LOGGER = logging.getLogger(__name__)

class ExtAppUserSearchService(ExtAPIInterface):
    """
    Service to handle external application user search requests for external API calls.
    The service only allows requesters with proper application role (with call_api permission)
    to perform the search.
    Ref API spec at https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Users+Search+API
    """

    def __init__(self, db: Session, requester: RequesterSchema, application_id: int, *args, **kwargs):
        super().__init__(requester, application_id, db=db, *args, **kwargs)

    def search_users(
        self,
        page_params: ExtUserSearchParamSchema,
        filter_params: ExtApplicationUserSearchSchema
    ) -> ExtUserSearchPagedResultsSchema:
        """
        For external Consumer API only.
        Searches users associated with the application based on filter_params and paginates results based on page_params.
        """
        if not self.is_request_allowed():
            error_msg = ("Programming error. This method is for external API only. "
                         "Router should have already checked the requester call API permission.")
            raise_http_exception(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                error_code=ERROR_CODE_INVALID_OPERATION,
                error_msg=error_msg,
            )

        LOGGER.debug(f"Searching users with filter_params: {filter_params}, page_params: {page_params}")

        # Base select statement
        user_role_stmt: Select = (
            select(FamUser)
            .join(FamUserRoleXref, FamUser.user_id == FamUserRoleXref.user_id)
            .join(FamRole, FamUserRoleXref.role_id == FamRole.role_id)
            .where(FamRole.application_id == self.application_id)
        )

        user_role_stmt: Select = self._apply_user_filters(user_role_stmt, filter_params)

        # Get total count of distinct users
        user_id_stmt: Select = user_role_stmt.with_only_columns(FamUser.user_id).distinct()
        total = self.db.execute(select(func.count()).select_from(user_id_stmt.subquery())).scalar()
        page = page_params.page or EXT_MIN_PAGE
        size = page_params.size or EXT_MIN_PAGE_SIZE
        page_count: int = (total + size - 1) // size if total > 0 else 1
        LOGGER.debug(f"Total users found: {total}, Page count: {page_count}")

        # Fetch paginated users with roles
        paged_stmt: Select = (
            user_role_stmt
            .options(
                # Eager load relationships
                joinedload(FamUser.fam_user_role_xref)
                .joinedload(FamUserRoleXref.role)
                .joinedload(FamRole.parent_role)
                .joinedload(FamRole.forest_client_relation)
            )
            .order_by(FamUser.user_name.asc())  # default sort by user_name ascending
            .distinct()
            .offset((page - 1) * size)
            .limit(size)
        )
        users: list[FamUser] = self.db.execute(paged_stmt).unique().scalars().all()
        LOGGER.debug(f"Found users: {[user.user_name for user in users]}")

        # Build results schema
        results: list[ExtApplicationUserSearchGetSchema] = self._build_user_search_results(users)
        LOGGER.debug(f"Returning {len(results)} users: {results}, for page {page}")

        meta = {
            "total": total,
            "pageCount": page_count,
            "page": page,
            "size": size
        }
        return ExtUserSearchPagedResultsSchema[ExtApplicationUserSearchGetSchema](meta=meta, users=results)

    def _apply_user_filters(self, user_role_stmt: Select, filter_params: ExtApplicationUserSearchSchema) -> Select:
        """
        Applies filtering to the base statement based on filter_params.
        """
        if filter_params.idp_type:
            user_role_stmt = self._apply_user_type_code_filter(user_role_stmt, filter_params.idp_type)
        if filter_params.idp_username:
            user_role_stmt = user_role_stmt.where(FamUser.user_name.ilike(f"%{filter_params.idp_username}%"))
        if filter_params.first_name:
            user_role_stmt = user_role_stmt.where(FamUser.first_name.ilike(f"%{filter_params.first_name}%"))
        if filter_params.last_name:
            user_role_stmt = user_role_stmt.where(FamUser.last_name.ilike(f"%{filter_params.last_name}%"))
        if filter_params.role:
            user_role_stmt = user_role_stmt.where(FamRole.role_name.in_(filter_params.role))
        return user_role_stmt

    def _build_user_search_results(self, users: list[FamUser]) -> list[ExtApplicationUserSearchGetSchema]:
        """
        Converts a list of FamUser model objects into list[ExtApplicationUserSearchGetSchema] objects.
        Example:
        "users": [{"firstName":"Ian","lastName":"Liu","idpUsername":"IANLIU","idpUserGuid":"A8888FAKEA999999FAKE123456789F",
                   "idpType":"IDIR","roles":[{"applicationName":"FOM_DEV","roleName":"FOM_ADMIN","roleDisplayName":"Admin",
                   "scopeType":null,"value":[]}]}]
        """
        results = []
        for user in users:
            roles_list = self._build_user_roles_list(user)
            user_schema = ExtApplicationUserSearchGetSchema(
                firstName=user.first_name,
                lastName=user.last_name,
                idpUsername=user.user_name,
                idpUserGuid=user.user_guid,
                idpType=self._map_user_type_code_to_idp_type(user.user_type_code),
                roles=roles_list
            )
            results.append(user_schema)
        return results

    def _build_user_roles_list(self, user: FamUser) -> List[ExtRoleWithScopeSchema]:
        """
        Builds the roles list schema for a given user.
        Example:
        [{"applicationName":"FOM_DEV","roleName":"FOM_REVIEWER","roleDisplayName":"Reviewer","scopeType":null,"value":[]},
         {"applicationName":"FOM_DEV","roleName":"FOM_SUBMITTER","roleDisplayName":"Submitter","scopeType":"FOREST_CLIENT",
         "value":["00001011","00002011"]}]
        """
        roles_list = []  # hold list of roles for the user in ExtRoleWithScopeSchema
        role_index = {}  # dict to look up existing role in roles_list
        for xref in user.fam_user_role_xref:
            role: FamRole = xref.role
            if role.application_id != self.application_id:
                continue

            role_name = role.role_name
            display_name = role.display_name
            scope_type = None
            current_scope_value = None
            has_parent_role = role.parent_role is not None
            if has_parent_role:
                role_name = role.parent_role.role_name  # use parent's role name for child roles
                display_name = role.parent_role.display_name  # use parent's display name for child roles
                scope_type = ScopeType.FOREST_CLIENT  # FAM currently only has FOREST_CLIENT scope type
                current_scope_value = role.forest_client_relation.forest_client_number

            # If role_name already exists, merge scope_value
            if role_name in role_index:
                idx = role_index[role_name]
                if current_scope_value not in roles_list[idx]["value"]:
                    roles_list[idx]["value"].append(current_scope_value)
            else:
                # add new role entry
                role_index[role_name] = len(roles_list)
                roles_list.append({
                    "applicationName": role.application.application_name,
                    "roleName": role_name,
                    "roleDisplayName": display_name,
                    "scopeType": scope_type,
                    "value": [current_scope_value] if current_scope_value else []
                })
        return roles_list

    def _map_user_type_code_to_idp_type(self, user_type_code: str) -> IDPType:
        """
        Maps FamUser.user_type_code to IdpType enum for API response.
        Example: 'I'(db) -> 'IDIR'(for API)
        """
        if user_type_code == UserType.IDIR:
            return IDPType.IDIR
        elif user_type_code == UserType.BCEID:
            return IDPType.BCEID
        else:
            return IDPType.BCSC

    def _apply_user_type_code_filter(self, user_role_stmt: Select, idp_type: IDPType) -> str:
        """
        Applies filtering to the statement based on the provided idp_type, maps to UserType for db filtering.
        Example: 'IDIR'(for API) -> 'I'(db)  => where(FamUser.user_type_code == UserType.IDIR)
        """
        if idp_type is None:
            return user_role_stmt

        elif idp_type == IDPType.IDIR:
            user_role_stmt = user_role_stmt.where(FamUser.user_type_code == UserType.IDIR)

        elif idp_type == IDPType.BCEID:
            user_role_stmt = user_role_stmt.where(FamUser.user_type_code == UserType.BCEID)

        else:
            user_role_stmt = user_role_stmt.where(
                and_(
                    FamUser.user_type_code != UserType.IDIR,
                    FamUser.user_type_code != UserType.BCEID
                )
            )

        return user_role_stmt