import logging
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from api.app import schemas
from api.app.constants import UserType
from api.app.models import model as models
from . import crud_utils as crud_utils

LOGGER = logging.getLogger(__name__)


def get_applications_by_granted_apps(db: Session, access_roles: List[str]) -> List[models.FamApplication]:
    """ Get applications based on access roles that are associated with.
        Note, this isn't to find the applications that the 'roles belong to'.

    :param access_roles: Cognito token custom groups (aka the Role(s) for FAM).
    :return: list of applications granted to view.
    """
    LOGGER.debug(f"Running get_applications_by_granted_app, access_roles: {access_roles}")

    # Filter out others and only contains Access Admin roles
    ACCESS_ADMIN_ROLE_SUFFIX = "_ADMIN"
    admin_access_roles = filter(
        lambda x: x.endswith(ACCESS_ADMIN_ROLE_SUFFIX), access_roles
    )
    app_names = crud_utils.replace_str_list(admin_access_roles, ACCESS_ADMIN_ROLE_SUFFIX, "")

    LOGGER.debug(f"Running db lookup for app name: {app_names}")

    fam_apps = (
        db.query(models.FamApplication)
        .filter(
            models.FamApplication.application_name.in_(app_names)
        )
        .distinct(models.FamApplication.application_name)
        .all()
    )
    LOGGER.debug(
        f"FamApplications: {fam_apps} {'found.' if fam_apps  else 'not found.'}"
    )
    return fam_apps


def get_application(db: Session, application_id: int):
    """gets a single application"""
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_id == application_id)
        .one_or_none()
    )
    return application


def get_application_by_name(db: Session, application_name: str):
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_name == application_name)
        .one_or_none()
    )
    return application


def get_application_roles(
    db: Session, application_id: int
) -> List[schemas.FamApplicationRole]:
    """Given a database session and an application id, will return a roles that
    have been defined for the application id.  Currently does not return any
    child roles.

    :param db: input database session object
    :param application_id: the application id who's roles are to be retrieved
    :return: orm FamRole model listing related roles that have been created
             for the given application.
    """
    # the application query below has to have parent_role_id == None, is None
    # doesn't translate to the correct query in sqlalchemy
    application = (
        db.query(models.FamRole)
        # .join(models.FamRole)
        # .options(load_only("application_id"))
        .filter(
            models.FamRole.application_id == application_id,
            models.FamRole.parent_role_id == None, # noqa
        ).all()
    )
    return application


def get_application_role_assignments(
    db: Session, application_id: int, requester: schemas.Requester
) -> List[models.FamUserRoleXref]:
    """query the user / role cross reference table to retrieve the role
    assignments.
    Delegated Admin will only see user role assignments by the roles granted for them.
    BCeID Delegated Admin will be further restricted for the same organization.

    :param db: database session
    :param application_id: the application id to retrieve the role assignments for.
    :param requester: the user who perform this request/action.
    :return: the user role assignments for the given application.
    """
    LOGGER.debug(f"Querying for user role assignments on app id:\
                  {application_id} by requester: {requester} ")

    # base query - users assigned to the application. This could be the case
    #              for [APP]_ADMIN.
    q = (
        db.query(models.FamUserRoleXref)
        .join(models.FamRole)
        .filter(models.FamRole.application_id == application_id)
    )

    if not crud_utils.is_app_admin(
        application_id=application_id,
        access_roles=requester.access_roles,
        db=db
    ):
        # subquery for finding out what roles (role_ids) the requester
        # (as an application delegated admin) is managing at for a specific application.
        role_ids_dlgdadmin_managed_subquery = (
            db.query(models.FamAccessControlPrivilege.role_id)
            .join(models.FamUser)
            .join(models.FamRole)
            .filter(
                models.FamUser.cognito_user_id == requester.cognito_user_id,
                models.FamRole.application_id == application_id
            )
            .subquery()
        )

        # filtered by the managed role for user_role assignments that the
        # requester (as an delegated admin) is allowed to see.
        q = q.filter(
            models.FamUserRoleXref.role_id.in_(
                select(role_ids_dlgdadmin_managed_subquery)
            )
        )

        if (requester.user_type_code == UserType.BCEID):
            # append additional filtering: A BCeID requester can only see
            # user_role records belonging to the same business organization.

            # Note, need to reassign to the variable from the base query.
            q = (
                q
                .join(models.FamUser)
                .filter(
                    models.FamUser.user_type_code == UserType.BCEID,
                    func.upper(
                        models.FamUser.business_guid
                    ) == requester.business_guid.upper()
                )
            )

    qresult = q.all()
    LOGGER.debug(f"Query for user role assignment complete with \
                 # of results = {len(qresult)}")
    return qresult


if __name__ == "__main__":
    # this is just demo code that can make it easier to develop crud functions
    # but technically should go into either a test or a fixture
    import database

    db = database.SessionLocal
    get_applications(db)
