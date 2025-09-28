import logging
from http import HTTPStatus

from api.app.constants import (ERROR_CODE_INVALID_OPERATION, EXT_MIN_PAGE,
                               EXT_MIN_PAGE_SIZE)
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.models.model import FamRole, FamUser, FamUserRoleXref
from api.app.schemas.ext.pagination import (ExtUserSearchPagedResultsSchema,
                                            ExtUserSearchParamSchema)
from api.app.schemas.ext.user_search import (ExtApplicationUserSearchGetSchema,
                                             ExtApplicationUserSearchSchema)
from api.app.schemas.requester import RequesterSchema
from api.app.utils.utils import raise_http_exception
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.selectable import Select

from .ext_api_interface import ExtAPIInterface

LOGGER = logging.getLogger(__name__)

class ExtAppUserSearchService(ExtAPIInterface):
    """
    Service to handle external application user search requests for external API calls.
    """

    def __init__(self, db: Session, requester: RequesterSchema, application_id: int, *args, **kwargs):
        super().__init__(requester, application_id, db=db, *args, **kwargs)

    def search_users(
        self,
        page_params: ExtUserSearchParamSchema,
        filter_params: ExtApplicationUserSearchSchema
    ) -> ExtUserSearchPagedResultsSchema:
        if not self.is_request_allowed():
            error_msg = ("Programming error occurred. This method is for external API only. "
                         "Router should have already checked the requester API call permission.")
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
            .options(joinedload(FamUser.fam_user_role_xref).joinedload(FamUserRoleXref.role))
            .distinct()
            .offset((page - 1) * size)
            .limit(size)
        )
        users: list[FamUser] = self.db.execute(paged_stmt).scalars().all()

        # Build results using helper
        results: list[ExtApplicationUserSearchGetSchema] = self._build_user_search_results(users)
        LOGGER.debug(f"Returning {len(results)} users: {results}, for page {page}")

        meta = {
            "total": total,
            "pageCount": page_count,
            "page": page,
            "size": size
        }
        return ExtUserSearchPagedResultsSchema[ExtApplicationUserSearchGetSchema](meta=meta, users=results)

    def _apply_user_filters(self, user_role_stmt: Select, filter_params: ExtUserSearchParamSchema) -> Select:
        """
        Applies filtering to the base statement based on filter_params.
        """
        if filter_params.idp_type:
            user_role_stmt = user_role_stmt.where(FamUser.user_type_code == filter_params.idp_type)
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
        Converts a list of FamUser objects into ExtApplicationUserSearchGetSchema objects.
        """
        results = []
        for user in users:
            roles_schema = []
            for xref in user.fam_user_role_xref:
                role = xref.role
                if role.application_id != self.application_id:
                    continue
                roles_schema.append({
                    "applicationName": None,  # Optionally fill from FamApplication if needed
                    "roleName": role.role_name,
                    "roleDisplayName": role.display_name,
                    "scopeType": None,
                    "value": []
                })
            user_schema = ExtApplicationUserSearchGetSchema(
                firstName=user.first_name,
                lastName=user.last_name,
                idpUsername=user.user_name,
                idpUserGuid=user.user_guid,
                idpType=user.user_type_code,
                roles=roles_schema
            )
            results.append(user_schema)
        return results
