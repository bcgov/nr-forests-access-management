import logging
from datetime import datetime
from typing import List

from api.app.constants import DelegatedAdminSortByEnum
from api.app.datetime_format import TIMESTAMP_FORMAT_DEFAULT
from api.app.models.model import (FamAccessControlPrivilege, FamForestClient,
                                  FamRole, FamUser)
from api.app.repositories.simple_paginate_repository import \
    SimplePaginateRepository
from api.app.schemas.pagination import (DelegatedAdminPageParamsSchema,
                                        PagedResultsSchema, PageParamsSchema)
from api.app.schemas.schemas import (FamAccessControlPrivilegeCreateDto,
                                     FamAccessControlPrivilegeGetResponse)
from sqlalchemy import Column, ColumnElement, func, or_, select
from sqlalchemy.orm import Session, joinedload

LOGGER = logging.getLogger(__name__)


class AccessControlPrivilegeRepository(SimplePaginateRepository):
    """
    Repository class with db operations for Delegated Admin role assignment
    (table=app_fam.fam_access_control_privilege).

    This class also inherits from "SimplePaginateRepository", an abstract base class which
    provides functionality for simple pagination for query on fam_access_control_privilege.
    """
    def __init__(self, db: Session):
        self.db = db
        super().__init__(db=db)

    def get_sort_by_column_mapping(self):
        """ provides/overrides implementation for 'SimplePaginateRepository' """
        return {
            DelegatedAdminSortByEnum.CREATE_DATE: FamAccessControlPrivilege.create_date, # default
            DelegatedAdminSortByEnum.USER_NAME: FamUser.user_name,
            DelegatedAdminSortByEnum.DOMAIN: FamUser.user_type_code,
            DelegatedAdminSortByEnum.EMAIL: FamUser.email,
            DelegatedAdminSortByEnum.FULL_NAME: FamUser.full_name,  # this is a hybrid column
            DelegatedAdminSortByEnum.ROLE_DISPLAY_NAME: FamRole.display_name,
            DelegatedAdminSortByEnum.FOREST_CLIENT_NUMBER: FamForestClient.forest_client_number
        }

    def get_filter_by_criteria(self, page_params: PageParamsSchema) -> ColumnElement[bool] | None:
        """
        Provides/overrides implementation for 'SimplePaginateRepository'.
        Based on 'search' keyword from page_params to build additional 'where' clause with
        'OR' sql condition,
        e.g., (app_fam.fam_user.user_name ILIKE %(user_name_1)s OR
            app_fam.fam_user.user_type_code ILIKE %(user_type_code_1)s OR
            app_fam.fam_user.email ILIKE %(email_1)s OR ...)
        to return for the query.
        """
        search_keyword = page_params.search
        filter_on_columns = self.get_sort_by_column_mapping().values()

        def operate_on_column(column: Column):
            """
            Determines column type to apply sql operator/function for filtering.
            """
            column_type = column.type.python_type
            if column_type is str:
                return column.ilike(f"%{search_keyword}%")
            elif column_type is datetime:
                return func.to_char(column, TIMESTAMP_FORMAT_DEFAULT).ilike(f"%{search_keyword}%")


        return (
            or_(
                # build where ... "OR" conditions for all mapped columns.
                *list(map(lambda column: operate_on_column(column), filter_on_columns))
            )
            if search_keyword is not None
            else None
        )

    def get_acp_by_user_id_and_role_id(
        self, user_id: int, role_id: int
    ) -> FamAccessControlPrivilege:
        return (
            self.db.query(FamAccessControlPrivilege)
            .filter(
                FamAccessControlPrivilege.user_id == user_id,
                FamAccessControlPrivilege.role_id == role_id,
            )
            .one_or_none()
        )

    def get_acp_by_id(
        self, access_control_privilege_id: int
    ) -> FamAccessControlPrivilege:
        return self.db.get(FamAccessControlPrivilege, access_control_privilege_id)

    def get_acp_by_application_id(
        self, application_id: int
    ) -> List[FamAccessControlPrivilege]:
        return (
            self.db.query(FamAccessControlPrivilege)
            .join(FamRole)
            .filter(FamRole.application_id == application_id)
            .all()
        )

    def get_paged_acp_by_application_id(
        self, application_id: int, page_params: DelegatedAdminPageParamsSchema
    ) -> PagedResultsSchema[FamAccessControlPrivilegeGetResponse]:
        """
        Paginates app_fam.fam_access_control_privilege for the
        application's Delegated Admin records.
        Arguments:
            application_id (int): The application's id, to find out the delegated admins
            belong to this application.

            page_params (DelegatedAdminPageParamsSchema): pagination parameters for query to
            return paged results.

        Returns:
            PagedResultsSchema[FamAccessControlPrivilegeGetResponse]: A paged results containing
            pagination metadata and a list of delegated admins assigned to this application.
        """
        base_query = (
            select(FamAccessControlPrivilege)
            .join(FamUser)
            .join(FamRole)
            .outerjoin(FamRole.client_number)
            .filter(FamRole.application_id == application_id)
        )
        return super().get_paginated_results(
            base_query=base_query, page_params=page_params, ResultSchema=FamAccessControlPrivilegeGetResponse
        )

    def create_access_control_privilege(
        self, fam_access_control_priviliege: FamAccessControlPrivilegeCreateDto
    ) -> FamAccessControlPrivilege:
        access_control_priviliege_dict = fam_access_control_priviliege.model_dump()
        db_item = FamAccessControlPrivilege(**access_control_priviliege_dict)
        self.db.add(db_item)
        self.db.flush()
        self.db.refresh(db_item)
        return db_item

    def delete_access_control_privilege(self, access_control_privilege_id: int) -> FamAccessControlPrivilege:
        record = (
            self.db.query(FamAccessControlPrivilege)
            .filter(
                FamAccessControlPrivilege.access_control_privilege_id
                == access_control_privilege_id
            )
            .one()
        )
        self.db.delete(record)
        self.db.flush()
        return record

    def get_user_delegated_admin_grants(self, user_id: int) -> List[FamRole]:
        """
        Find out from `app_fam.fam_access_control_privilege` the applications' roles
            the user is allow to grant.

        :param user_id: primary id that is associated with the user.
        :return: List of "roles" the user is allowed to grant or None.
        """
        return (
            self.db.query(FamRole)
            .options(joinedload(FamRole.application))  # also loads relationship
            .select_from(FamAccessControlPrivilege)
            .join(FamAccessControlPrivilege.role)
            .join(FamAccessControlPrivilege.user)
            .filter(FamAccessControlPrivilege.user_id == user_id)
            .order_by(FamRole.application_id, FamRole.role_id)
            .all()
        )
