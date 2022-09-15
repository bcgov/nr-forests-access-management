import logging
from http import HTTPStatus
from typing import Optional

from api.app import constants as famConstants
from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas
from . import crud_role, crud_user, crud_forest_client, crudUtils

LOGGER = logging.getLogger(__name__)


def createFamUserRoleAssignment(
    request: schemas.FamUserRoleAssignmentCreate, db: Session
):
    """
    Create fam_user_role_xref Association

    For initial MVP version:
        FAM api will do a smart insertion to fam_user_role_xref(and fam_user, fam_role, fam_forest_client)
        assume and skip some verification/lookup; such as 'forest_client' lookup and 'user' lookup.
    """
    LOGGER.debug(f"Request for user role assignment: {request}.")

    # Verify user_type in enum (IDIR, BCEID)
    if (
        request.user_type != famConstants.UserType.IDIR
        and request.user_type != famConstants.UserType.BCEID
    ):
        error_msg = f"Invalid user type: {request.user_type}."
        crudUtils.raiseHTTPException(HTTPStatus.BAD_REQUEST, error_msg)

    # Determine if user already exists or add a new user.
    fam_user = crud_user.findOrCreate(db, request.user_type, request.user_name)

    # Verify if role exists.
    fam_role = crud_role.getFamRole(db, request.role_id)
    if not fam_role:
        error_msg = f"Role id {request.role_id} does not exist."
        crudUtils.raiseHTTPException(HTTPStatus.BAD_REQUEST, error_msg)
    LOGGER.debug(
        f"Role for user_role assignment found: {fam_role.role_name} ({fam_role.role_id})."
    )

    child_role: Optional(models.FamRole) = None
    if request.client_number_id:
        LOGGER.debug(
            f"Forest Client Id {request.client_number_id} present "
            "in request to assign a forest client role."
        )

        child_role = findOrCreateChildRole(db, request.client_number_id, fam_role)

    # Role Id for associating with user
    associate_role_id = child_role.role_id if child_role else fam_role.role_id

    fam_user_role_xref = findOrCreate(db, fam_user.user_id, associate_role_id)
    LOGGER.debug(
        f"User/Role assignment executed successfully: {fam_user_role_xref.__dict__}"
    )
    return fam_user_role_xref


def findOrCreate(db: Session, user_id: int, role_id: int):
    LOGGER.debug(
        f"FamUserRoleXref - 'findOrCreate' with user_id: {user_id}, role_id: {role_id}."
    )

    fam_user_role_xref = getUserRolebyUserIdAndRoleId(db, user_id, role_id)

    if not fam_user_role_xref:
        new_fam_user_role: models.FamUserRoleXref = models.FamUserRoleXref(
            **{
                "user_id": user_id,
                "role_id": role_id,
                "create_user": famConstants.FAM_PROXY_API_USER,
            }
        )
        db.add(new_fam_user_role)
        db.flush()
        LOGGER.debug(f"New FamUserRoleXref added for {new_fam_user_role.__dict__}")
        return new_fam_user_role

    LOGGER.debug(
        f"FamUserRoleXref already exists with id: {fam_user_role_xref.user_role_xref_id}."
    )
    return fam_user_role_xref


def getUserRolebyUserIdAndRoleId(
    db: Session, user_id: int, role_id: int
) -> models.FamUserRoleXref:
    famUserRole = (
        db.query(models.FamUserRoleXref)
        .filter(
            models.FamUserRoleXref.user_id == user_id
            and models.FamUserRoleXref.role_id == role_id
        )
        .one_or_none()
    )
    return famUserRole


def constructForestClientRoleName(parent_role_name: str, client_number_id: int):
    return f"{parent_role_name}_{client_number_id}"


def constructForestClientRolePurpose(
    parent_role_purpose: str, client_name: str, client_number_id: int
):
    return f"{parent_role_purpose} for {client_name} ({client_number_id})"


def findOrCreateChildRole(
    db: Session, client_number_id: int, parent_role: models.FamRole
):
    # Note, this is current implementation for fam_forest_client as to programmatically
    # insert a record into the table. Later FAM will be interfacing with Forest
    # Client API, thus the way to insert a record will cahnge.
    forest_client = crud_forest_client.findOrCreate(db, client_number_id)

    # Verify if Forest Client role (child role) exist
    forest_client_role_name = constructForestClientRoleName(
        parent_role.role_name, client_number_id
    )
    forest_client_child_role = crud_role.getFamRoleByRoleName(
        db,
        forest_client_role_name,
    )
    LOGGER.debug(
        "Forest Client child role for role_name "
        f"'{forest_client_role_name}':"
        f" {'Does not exist' if not forest_client_child_role else 'Exists'}"
    )

    if not forest_client_child_role:
        # Note, later implementation for forest-client child role will be based on a
        # boolean column from the parent role that requires forest-client child role.
        child_role = crud_role.createFamRole(
            schemas.FamRoleCreate(
                **{
                    "parent_role_id": parent_role.role_id,
                    "application_id": parent_role.application_id,
                    "client_number_id": client_number_id,
                    "role_name": forest_client_role_name,
                    "role_purpose": constructForestClientRolePurpose(
                        parent_role.role_purpose,
                        forest_client.client_name,
                        client_number_id,
                    ),
                    "create_user": famConstants.FAM_PROXY_API_USER,
                }
            ),
            db,
        )
        LOGGER.debug(
            f"Child role {child_role.role_id} added for parent role "
            f"{parent_role.role_name}({child_role.parent_role_id})."
        )
