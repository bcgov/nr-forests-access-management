import logging
from http import HTTPStatus

from api.app import constants as famConstants
from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas
from . import crud_user, crud_utils, crud_application

LOGGER = logging.getLogger(__name__)


def create_application_admin(
    db: Session, request: schemas.FamAppAdminCreate, requester: str
) -> schemas.FamAppAdminGet:
    """
    Create fam_user_role_xref Association

    For initial MVP version:
        FAM api will do a smart insertion to fam_user_role_xref
        (and fam_user, fam_role, fam_forest_client)
        assume and skip some verification/lookup; such as 'forest_client'
        lookup and 'user' lookup.
    """
    LOGGER.debug(f"Request for user role assignment: {request}.")

    # Verify user_type_code in enum (IDIR, BCEID)
    if (
        request.user_type_code != famConstants.UserType.IDIR
        and request.user_type_code != famConstants.UserType.BCEID
    ):
        error_msg = f"Invalid user type: {request.user_type_code}."
        crud_utils.raise_http_exception(HTTPStatus.BAD_REQUEST, error_msg)

    # Determine if user already exists or add a new user.
    fam_user = crud_user.find_or_create(
        db, request.user_type_code, request.user_name, requester
    )

    # Verify if application exists.
    fam_application = crud_application.get_application(db, request.application_id)
    if not fam_application:
        error_msg = f"Application id {request.fam_application} does not exist."
        crud_utils.raise_http_exception(HTTPStatus.BAD_REQUEST, error_msg)
    LOGGER.debug(
        f"Application for fam_admin assignment found: {fam_application.application_name}"
        + f"({fam_application.application_id})."
    )

    # Verify if user is admin already
    fam_application_admin_user = get_application_admin(
        db, request.application_id, fam_user.user_id
    )
    print("if user is admin", fam_application_admin_user)
    if fam_application_admin_user:
        LOGGER.debug(
            "FamApplicationAdmin already exists with id: "
            + f"{fam_application_admin_user.application_admin_id}."
        )
        error_msg = "User is admin already."
        crud_utils.raise_http_exception(HTTPStatus.CONFLICT, error_msg)
    else:
        # Create application admin if user is not admin yet
        fam_application_admin_user = (
            create_application_admin_assignment(
                db, request.application_id, fam_user.user_id, requester
            )
        )

    fam_application_admin_user_dict = fam_application_admin_user.__dict__
    app_admin_user_assignment = schemas.FamAppAdminGet(
        **fam_application_admin_user_dict
    )
    LOGGER.debug(
        f"Application admin user assignment executed successfully: {app_admin_user_assignment}"
    )
    return app_admin_user_assignment


def get_application_admin(db: Session, application_id: int, user_id: int):
    return (
        db.query(models.FamApplicationAdmin)
        .filter(
            models.FamApplicationAdmin.application_id == application_id,
            models.FamApplicationAdmin.user_id == user_id,
        )
        .one_or_none()
    )


def create_application_admin_assignment(
    db: Session, application_id: int, user_id: int, requester: str
):
    new_fam_application_admin: models.FamApplicationAdmin = models.FamApplicationAdmin(
        **{
            "user_id": user_id,
            "application_id": application_id,
            "create_user": requester,
        }
    )
    db.add(new_fam_application_admin)
    db.flush()
    db.refresh(new_fam_application_admin)
    LOGGER.debug(
        f"New FamApplicationAdmin added for {new_fam_application_admin.__dict__}"
    )
    return new_fam_application_admin
