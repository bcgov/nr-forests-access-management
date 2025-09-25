import logging
from datetime import datetime

from api.app.constants import UserRoleSortByEnum, UserType
from api.app.crud.services.paginate_service import PaginateService
from api.app.datetime_format import TIMESTAMP_FORMAT_DEFAULT
from api.app.decorators.forest_client_dec import post_sync_forest_clients_dec
from api.app.models import model as models
from api.app.schemas import (FamApplicationUserRoleAssignmentGetSchema,
                             RequesterSchema)
from api.app.schemas.pagination import (PagedResultsSchema,
                                        UserRolePageParamsSchema)
from sqlalchemy import Column, asc, desc, func, or_, select
from sqlalchemy.orm import Session

from . import crud_utils as crud_utils

LOGGER = logging.getLogger(__name__)

# Local constant only, for application user/role sorting/filtering query,
# provides mapping for sortBy/filtered columns mapped to model columns.
USER_ROLE_SORT_BY_MAPPED_COLUMN = {
    UserRoleSortByEnum.CREATE_DATE: models.FamUserRoleXref.create_date, # default
    UserRoleSortByEnum.USER_NAME: models.FamUser.user_name,
    UserRoleSortByEnum.DOMAIN: models.FamUser.user_type_code,
    UserRoleSortByEnum.EMAIL: models.FamUser.email,
    UserRoleSortByEnum.FULL_NAME: models.FamUser.full_name,  # this is a hybrid column
    UserRoleSortByEnum.ROLE_DISPLAY_NAME: models.FamRole.display_name,
    UserRoleSortByEnum.FOREST_CLIENT_NUMBER: models.FamForestClient.forest_client_number
}

def get_application(db: Session, application_id: int):
    """gets a single application"""
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_id == application_id)
        .one_or_none()
    )
    return application


def __build_filter_criteria(page_params: UserRolePageParamsSchema):
    """
    Based on 'search' keyword from page_params to build additional 'where'
    clause. In this endpoint pagination case, all mapped columns to be
    filtered on can apply with 'ilike' (case-insensitive operator) with
    'OR' sql condition,
    e.g., (app_fam.fam_user.user_name ILIKE %(user_name_1)s OR
           app_fam.fam_user.user_type_code ILIKE %(user_type_code_1)s OR
           app_fam.fam_user.email ILIKE %(email_1)s OR ...)
    to return for the query.
    """
    search_keyword = page_params.search
    filter_on_columns = USER_ROLE_SORT_BY_MAPPED_COLUMN.values()

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

@post_sync_forest_clients_dec
def get_application_role_assignments(
    db: Session, application_id: int, requester: RequesterSchema, page_params: UserRolePageParamsSchema
) -> PagedResultsSchema[FamApplicationUserRoleAssignmentGetSchema]:
    """query the user / role cross reference table to retrieve the role
    assignments.
    Delegated Admin will only see user role assignments by the roles granted for them.
    BCeID Delegated Admin will be further restricted for the same organization.

    :param db: database session
    :param application_id: the application id to retrieve the role assignments for.
    :param requester: the user who perform this request/action.
    :param page_params: parameters for pagination, sorting and filtering.
    :return: the paged user role assignments for the given application.
    """
    LOGGER.debug(
        f"Querying for user role assignments on app id: {application_id} by requester: {requester} "
    )

    query_user_roles_by_app_privilege = __query_user_roles_by_app_privilege(
        db, requester, application_id
    )

    paginated_service = PaginateService(
        db, query_user_roles_by_app_privilege,
        __build_filter_criteria(page_params),
        USER_ROLE_SORT_BY_MAPPED_COLUMN,
        page_params
    )
    qresult = paginated_service.get_paginated_results(FamApplicationUserRoleAssignmentGetSchema)
    LOGGER.debug(
        f"Querying for user role assignment completed with # of results = {len(qresult.results)}"
    )
    return qresult

def get_application_role_assignments_no_paging(
    db: Session, application_id: int, requester: RequesterSchema
) -> list[FamApplicationUserRoleAssignmentGetSchema]:
    """
    The function is almost the same as 'get_application_role_assignments'; but it will query the
    user role assignments for a given application with full result no pagination.
    Note, it does not apply 'post_sync_forest_clients_dec' decorator for 'forest client name'
    external api sync.

    :param requester: the user who perform this request/action.
    :param application_id: the application id to retrieve the role assignments for.
    """
    query_user_roles_by_app_permission = __query_user_roles_by_app_privilege(
        db, requester, application_id
    )

    qresults = db.scalars(query_user_roles_by_app_permission).all()
    results = [FamApplicationUserRoleAssignmentGetSchema.model_validate(result) for result in qresults]
    return results

def __query_user_roles_by_app_privilege(db: Session, requester: RequesterSchema, application_id: int) -> select:
    """
    The 'select query' construct for user role assignments for a given application
    based on the requester's privilege.
    :param requester: the user who perform this request/action.
    :param application_id: the application id to retrieve the role assignments for.
    :return: the query construct for user role assignments for a given application. Depending on
             the user's privilege, the query will be filtered accordingly.

            APP_ADMIN: will see all user role assignments for the application.
            DELEGATED_ADMIN: will see user role assignments for the application based on the roles
                privilege they have been granted. For BCeID delegated admin: will further be restricted
                to see only user role assignments for user within the same business organization.
    """
    # base query - users assigned to the application. This could be the case
    #              for [APP]_ADMIN.
    q = (
        select(models.FamUserRoleXref)
        .join(models.FamUser)
        .join(models.FamRole)
        .outerjoin(models.FamRole.forest_client_relation)
        .filter(models.FamRole.application_id == application_id)
    )

    if not crud_utils.is_app_admin(
        application_id=application_id, access_roles=requester.access_roles, db=db
    ):
        # subquery for finding out what roles (role_ids) the requester
        # (as an application delegated admin) is managing at for a specific application.
        role_ids_dlgdadmin_managed_subquery = (
            select(models.FamAccessControlPrivilege.role_id)
            .join(models.FamUser)
            .join(models.FamRole)
            .where(
                models.FamUser.cognito_user_id == requester.cognito_user_id,
                models.FamRole.application_id == application_id,
            )
            .subquery()
        )

        # filtered by the managed role for user_role assignments that the
        # requester (as an delegated admin) is allowed to see.
        q = q.where(
            models.FamUserRoleXref.role_id.in_(
                role_ids_dlgdadmin_managed_subquery
            )
        )

        if requester.user_type_code == UserType.BCEID:
            # append additional filtering: A BCeID requester can only see
            # user_role records belonging to the same business organization.

            # Note, need to reassign to the variable from the base query.
            q = q.where(
                models.FamUser.user_type_code == UserType.BCEID,
                func.upper(models.FamUser.business_guid)
                == requester.business_guid.upper(),
            )
    return q

def get_application_by_app_client_id(db: Session, app_client_id: str):
    """
    Retrieve a FamApplication by its app_client_id (cognito_client_id).
    :param db: SQLAlchemy session
    :param app_client_id: The cognito_client_id
    :return: FamApplication instance or None
    """
    stmt = (
        select(models.FamApplication)
        .join(models.FamApplicationClient, models.FamApplication.application_id == models.FamApplicationClient.application_id)
        .where(models.FamApplicationClient.cognito_client_id == app_client_id)
    )
    result = db.execute(stmt).scalars().one_or_none()
    return result