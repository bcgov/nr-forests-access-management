import logging
from typing import List

from api.app.schemas import RequesterSchema, FamApplicationUserRoleAssignmentGetSchema
from api.app.constants import UserType
from api.app.models import (
    FamApplicationModel,
    FamRoleModel,
    FamUserModel,
    FamUserRoleXrefModel,
    FamAccessControlPrivilegeModel,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import crud_utils as crud_utils

LOGGER = logging.getLogger(__name__)


def get_application(db: Session, application_id: int):
    """gets a single application"""
    application = (
        db.query(FamApplicationModel)
        .filter(FamApplicationModel.application_id == application_id)
        .one_or_none()
    )
    return application


def get_application_role_assignments(
    db: Session, application_id: int, requester: RequesterSchema
) -> List[FamApplicationUserRoleAssignmentGetSchema]:
    """query the user / role cross reference table to retrieve the role
    assignments.
    Delegated Admin will only see user role assignments by the roles granted for them.
    BCeID Delegated Admin will be further restricted for the same organization.

    :param db: database session
    :param application_id: the application id to retrieve the role assignments for.
    :param requester: the user who perform this request/action.
    :return: the user role assignments for the given application.
    """
    LOGGER.debug(
        f"Querying for user role assignments on app id:\
                  {application_id} by requester: {requester} "
    )

    # base query - users assigned to the application. This could be the case
    #              for [APP]_ADMIN.
    q = (
        db.query(FamUserRoleXrefModel)
        .join(FamRoleModel)
        .filter(FamRoleModel.application_id == application_id)
    )

    if not crud_utils.is_app_admin(
        application_id=application_id, access_roles=requester.access_roles, db=db
    ):
        # subquery for finding out what roles (role_ids) the requester
        # (as an application delegated admin) is managing at for a specific application.
        role_ids_dlgdadmin_managed_subquery = (
            db.query(FamAccessControlPrivilegeModel.role_id)
            .join(FamUserModel)
            .join(FamRoleModel)
            .filter(
                FamUserModel.cognito_user_id == requester.cognito_user_id,
                FamRoleModel.application_id == application_id,
            )
            .subquery()
        )

        # filtered by the managed role for user_role assignments that the
        # requester (as an delegated admin) is allowed to see.
        q = q.filter(
            FamUserRoleXrefModel.role_id.in_(
                select(role_ids_dlgdadmin_managed_subquery)
            )
        )

        if requester.user_type_code == UserType.BCEID:
            # append additional filtering: A BCeID requester can only see
            # user_role records belonging to the same business organization.

            # Note, need to reassign to the variable from the base query.
            q = q.join(FamUserModel).filter(
                FamUserModel.user_type_code == UserType.BCEID,
                func.upper(FamUserModel.business_guid)
                == requester.business_guid.upper(),
            )

    qresult = q.all()
    LOGGER.debug(
        f"Query for user role assignment complete with \
                 # of results = {len(qresult)}"
    )
    return qresult
