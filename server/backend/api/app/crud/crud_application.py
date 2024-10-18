import logging

from api.app.constants import SortOrderEnum, UserRoleSortByEnum, UserType
from api.app.crud.services.paginate_service import PaginateService
from api.app.models import model as models
from api.app.schemas import (FamApplicationUserRoleAssignmentGetSchema,
                             RequesterSchema)
from api.app.schemas.pagination import (PagedResultsSchema,
                                        UserRolePageParamsSchema)
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from . import crud_utils as crud_utils

LOGGER = logging.getLogger(__name__)


def get_application(db: Session, application_id: int):
    """gets a single application"""
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_id == application_id)
        .one_or_none()
    )
    return application


def build_order_by_construct(page_params: UserRolePageParamsSchema):
    # currently only 1 sortBy column.
    sort_by = page_params.sort_by
    sort_order = page_params.sort_order
    column = models.FamUser.user_name  # default

    if sort_by == UserRoleSortByEnum.DOMAIN:
        column = models.FamUser.user_type_code
    elif sort_by == UserRoleSortByEnum.EMAIL:
        column = models.FamUser.email
    elif sort_by == UserRoleSortByEnum.ROLE_DISPLAY_NAME:
        column = models.FamRole.display_name
    elif sort_by == UserRoleSortByEnum.FOREST_CLIENT_NUMBER:
        column = models.FamForestClient.forest_client_number
    elif sort_by == UserRoleSortByEnum.FULL_NAME:
        column = models.FamUser.full_name  # this is a hybrid column

    LOGGER.info(f"column: {column}")
    return asc(column) if sort_order == SortOrderEnum.ASC else desc(column)


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

    # base query - users assigned to the application. This could be the case
    #              for [APP]_ADMIN.
    q = (
        select(models.FamUserRoleXref)
        .join(models.FamUser)
        .join(models.FamRole)
        .outerjoin(models.FamRole.client_number)
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
            q = q.join(models.FamUser).where(
                models.FamUser.user_type_code == UserType.BCEID,
                func.upper(models.FamUser.business_guid)
                == requester.business_guid.upper(),
            )

    paginated_service = PaginateService(db, q, build_order_by_construct(page_params), page_params)
    qresult = paginated_service.get_paginated_results(FamApplicationUserRoleAssignmentGetSchema)
    LOGGER.debug(
        f"Query for user role assignment complete with \
                 # of results = {len(qresult.results)}"
    )
    return qresult