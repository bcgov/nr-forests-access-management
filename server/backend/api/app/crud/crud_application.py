import datetime
import logging
from typing import List

from sqlalchemy.orm import Session, load_only, joinedload

import api.app.constants as constants
from api.app.models import model as models

from .. import schemas
from . import crud_utils as crud_utils

LOGGER = logging.getLogger(__name__)


def get_applications(db: Session):
    """runs query to return all the community health service areas and the
    metadata about how many times they have been queried and when

    :param db: database session
    :type db: Session
    :return: list of sql alchemy data objects
    :rtype: list
    """
    LOGGER.debug("running get_applications")
    LOGGER.debug(f"db: {type(db)}")
    # LOGGER.debug(f"db parameters {db.parameters}")
    fam_apps = db.query(models.FamApplication).all()
    LOGGER.debug(f"famApplications: {fam_apps}, {type(fam_apps)}")
    return fam_apps


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
    db: Session, application_id: int
) -> List[models.FamUserRoleXref]:
    """query the user / role cross reference table to retrieve the role
    assignments

    :param db: database session
    :type db: Session
    :param application_id: the application id that we want to retrieve the role
        assignments for.
    :return: the role assignments for the given application

    """
    LOGGER.debug(f"Query for user role assignments for app id: {application_id}")

    crossref = (
        db.query(models.FamUserRoleXref)
        .join(models.FamRole)
        .filter(models.FamRole.application_id == application_id)
        .all()
    )

    LOGGER.debug(f"Query for user role assignment complete with # of results = {len(crossref)}")
    return crossref


def get_application_id_by_role_id(db: Session, role_id):
    # question: why we need to go to fam_application table?
    # the fam_role table has the application_id already

    application_id =\
        db.query(models.FamApplication.application_id)\
        .join(models.FamRole)\
        .filter(models.FamRole.role_id == role_id)\
        .scalar()

    return application_id


def get_application_id_by_user_role_xref_id(db: Session, user_role_xref_id):
    application_id =\
        db.query(models.FamApplication.application_id)\
        .join(models.FamRole)\
        .join(models.FamUserRoleXref)\
        .filter(models.FamUserRoleXref.user_role_xref_id == user_role_xref_id)\
        .scalar()

    return application_id


if __name__ == "__main__":
    # this is just demo code that can make it easier to develop crud functions
    # but technically should go into either a test or a fixture
    import database

    db = database.SessionLocal
    get_applications(db)
