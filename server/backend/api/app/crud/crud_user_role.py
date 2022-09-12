import logging
from http import HTTPStatus
from typing import Optional

from api.app import constants as famConstants
from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas
from . import crud_role, crud_user, crudUtils

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
    fam_user = crud_user.getFamUserByDomainAndName(
        db, request.user_type, request.user_name
    )
    if not fam_user:
        requestUser = schemas.FamUser(
            **{
                "user_type": request.user_type,
                "user_name": request.user_name,
                "create_user": famConstants.FAM_SYSTEM_USER,
            }
        )
        fam_user = crud_user.createFamUser(requestUser, db)
    LOGGER.debug(f"User for user_role assignment: {fam_user.user_id}.")

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
        forest_client: models.FamForestClient = (
            db.query(models.FamForestClient)
            .filter(
                models.FamForestClient.client_number_id == request.client_number_id
            )
            .one_or_none()
        )

        # Note, current mvp implementation is: if Forest Client does not exist, insert one.
        # Later when fully integrated with forest-client api then it can be verified against the source.
        if not forest_client:
            LOGGER.debug(
                f"Forest Client with Id {request.client_number_id} "
                "does not exist, add a new Forest Client."
            )
            new_fam_forest_client: models.FamForestClient = models.FamForestClient(
                **{
                    "client_number_id": request.client_number_id,
                    "client_name": famConstants.DUMMY_FOREST_CLIENT_NAME,
                    "create_user": famConstants.FAM_SYSTEM_USER,
                }
            )
            db.add(new_fam_forest_client)
            db.flush()
            LOGGER.debug(
                f"New Forest Client {new_fam_forest_client.client_number_id} added."
            )

        # Verify if Forest Client role exist
        forest_client_child_role = crud_role.getFamRoleByRoleName(
            db,
            constructForestClientRoleName(fam_role.role_name, request.client_number_id),
        )
        LOGGER.debug(f"forest_client_child_roles: {forest_client_child_role}")

        if not forest_client_child_role:
            # Note, later implementation for forest-client child role will be based on a
            # boolean column from the parent role that requires forest-client child role.
            child_role = crud_role.createFamRole(
                schemas.FamRole(
                    {
                        "parent_role_id": fam_role.role_id,
                        "application_id": fam_role.application_id,
                        "client_number_id": request.client_number_id,
                        "role_name": constructForestClientRoleName(
                            fam_role.role_name, request.client_number_id
                        ),
                        "role_purpose": constructForestClientRolePurpose(
                            fam_role.role_purpose,
                            forest_client.client_name,
                            request.client_number_id,
                        ),
                    }
                ),
                db,
            )
            LOGGER.debug(
                f"Child role {child_role.role_id} added for parent role "
                "{fam_role.role_name}(${child_role.parent_role_id})."
            )

        else:
            child_role = forest_client_child_role

    # Role Id for associating with user
    associate_role_id = child_role.role_id if child_role else fam_role.role_id

    # Check if the user/role assignment (fam_user_role_xref) already exists.
    fam_user_role_xref = getUserRolebyUserIdAndRoleId(
        db, fam_user.user_id, associate_role_id
    )
    if fam_user_role_xref:
        LOGGER.debug(
            f"User/Role assignment already exists with id: {fam_user_role_xref.user_role_xref_id}."
        )
        return fam_user_role_xref

    # Finally, assign user with role/child-role
    new_fam_user_role: models.FamUserRoleXref = models.FamUserRoleXref(
        {
            "user_id": fam_user.user_id,
            "role_id": associate_role_id,
            "create_user": famConstants.FAM_SYSTEM_USER,
        }
    )
    db.add(new_fam_user_role)
    db.commit()
    return new_fam_user_role


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
