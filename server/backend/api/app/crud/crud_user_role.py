import logging
from http import HTTPStatus
from typing import List

from api.app import constants as famConstants
from api.app import schemas
from api.app.crud import crud_forest_client, crud_role, crud_user, crud_utils
from api.app.integration.forest_client.forest_client import ForestClientService
from api.app.models import model as models
from api.app.utils.utils import raise_http_exception
from api.app.crud.validator.forest_client_validator import (
    forest_client_active,
    forest_client_number_exists,
    get_forest_client_status,
)
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


def create_user_role_assignment_many(
    db: Session,
    request: schemas.FamUserRoleAssignmentCreate,
    target_user: schemas.TargetUser,
    requester: str,
) -> schemas.FamUserRoleAssignmentGet:
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
        raise_http_exception(
            error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
            error_msg=error_msg,
        )

    # Determine if user already exists or add a new user.
    fam_user = crud_user.find_or_create(
        db, request.user_type_code, request.user_name, request.user_guid, requester
    )
    fam_user = crud_user.update_user_properties_from_verified_target_user(
        db, fam_user.user_id, target_user, requester
    )

    # Verify if role exists.
    fam_role = crud_role.get_role(db, request.role_id)
    if not fam_role:
        error_msg = f"Role id {request.role_id} does not exist."
        raise_http_exception(
            error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
            error_msg=error_msg,
        )

    LOGGER.debug(
        f"Role for user_role assignment found: {fam_role.role_name}"
        + f"({fam_role.role_id})."
    )

    # Role is a 'Concrete' type, then create role assignment directly with the role.
    # Role is a 'Abstract' type, create role assignment with forst client child role.
    require_child_role = (
        fam_role.role_type_code == famConstants.RoleType.ROLE_TYPE_ABSTRACT
    )

    create_return_list: List[schemas.FamUserRoleAssignmentCreateResponse] = []

    if require_child_role:
        LOGGER.debug(
            f"Role {fam_role.role_name} requires child role "
            "for user/role assignment."
        )

        if (
            not hasattr(request, "forest_client_numbers")
            or request.forest_client_numbers is None
            or len(request.forest_client_numbers) < 1
        ):
            error_msg = (
                "Invalid user role assignment request, missing forest client number."
            )
            raise_http_exception(
                error_code=famConstants.ERROR_CODE_MISSING_KEY_ATTRIBUTE,
                error_msg=error_msg,
            )

        api_instance_env = crud_utils.use_api_instance_by_app(fam_role.application)
        forest_client_integration_service = ForestClientService(api_instance_env)

        for forest_client_number in request.forest_client_numbers:
            # validate the forest client number
            forest_client_validator_return = (
                forest_client_integration_service.find_by_client_number(
                    forest_client_number
                )
            )

            if not forest_client_number_exists(forest_client_validator_return):
                error_msg = (
                    "Invalid role assignment request. "
                    + f"Forest Client Number {forest_client_number} does not exist."
                )
                raise_http_exception(
                    error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                    error_msg=error_msg,
                )

            if not forest_client_active(forest_client_validator_return):
                error_msg = (
                    f"Invalid role assignment request. Forest client number {forest_client_number} is not in active status:"
                    + f"{get_forest_client_status(forest_client_validator_return)}"
                )
                raise_http_exception(
                    error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                    error_msg=error_msg,
                )

            # Check if child role exists or add a new child role
            child_role = find_or_create_forest_client_child_role(
                db, forest_client_number, fam_role, requester
            )
            # Role for associating with user
            associate_role = child_role if require_child_role else fam_role

            # Create user/role assignment
            handle_create_return = create_user_role_assignment(
                db, fam_user, associate_role, requester
            )
            create_return_list.append(handle_create_return)
    else:
        # Create user/role assignment
        handle_create_return = create_user_role_assignment(
            db, fam_user, fam_role, requester
        )
        create_return_list.append(handle_create_return)

    LOGGER.debug(f"User/Role assignment executed successfully: {create_return_list}")
    return create_return_list


def create_user_role_assignment(
    db: Session, user: models.FamUser, role: models.FamRole, requester: str
):
    create_user_role_assginment_return = None
    fam_user_role_xref = get_use_role_by_user_id_and_role_id(
        db, user.user_id, role.role_id
    )
    xref_dict = {"application_id": role.application_id, "user": user, "role": role}

    if fam_user_role_xref:
        xref_dict = {**fam_user_role_xref.__dict__, **xref_dict}
        error_msg = (
            f"Role {fam_user_role_xref.role.role_name} already assigned to user {fam_user_role_xref.user.user_name}. "
            + f"FamUserRoleXref already exists with id: {fam_user_role_xref.user_role_xref_id}"
        )
        create_user_role_assginment_return = (
            schemas.FamUserRoleAssignmentCreateResponse(
                **{
                    "status_code": HTTPStatus.CONFLICT,
                    "detail": schemas.FamApplicationUserRoleAssignmentGet(**xref_dict),
                    "error_message": error_msg,
                }
            )
        )
    else:
        fam_user_role_xref = create(db, user.user_id, role.role_id, requester)
        xref_dict = {**fam_user_role_xref.__dict__, **xref_dict}
        create_user_role_assginment_return = (
            schemas.FamUserRoleAssignmentCreateResponse(
                **{
                    "status_code": HTTPStatus.OK,
                    "detail": schemas.FamApplicationUserRoleAssignmentGet(**xref_dict),
                }
            )
        )

    return create_user_role_assginment_return


def delete_fam_user_role_assignment(db: Session, user_role_xref_id: int):
    record = (
        db.query(models.FamUserRoleXref)
        .filter(models.FamUserRoleXref.user_role_xref_id == user_role_xref_id)
        .one()
    )
    db.delete(record)
    db.flush()


def create(db: Session, user_id: int, role_id: int, requester: str):
    LOGGER.debug(
        f"FamUserRoleXref - 'create' with user_id: {user_id}, " + f"role_id: {role_id}."
    )

    new_fam_user_role: models.FamUserRoleXref = models.FamUserRoleXref(
        **{
            "user_id": user_id,
            "role_id": role_id,
            "create_user": requester,
        }
    )
    db.add(new_fam_user_role)
    db.flush()
    db.refresh(new_fam_user_role)
    LOGGER.debug(f"New FamUserRoleXref added for {new_fam_user_role.__dict__}")
    return new_fam_user_role


def get_use_role_by_user_id_and_role_id(
    db: Session, user_id: int, role_id: int
) -> models.FamUserRoleXref:
    user_role = (
        db.query(models.FamUserRoleXref)
        .filter(
            models.FamUserRoleXref.user_id == user_id,
            models.FamUserRoleXref.role_id == role_id,
        )
        .one_or_none()
    )
    return user_role


def construct_forest_client_role_name(parent_role_name: str, forest_client_number: str):
    return f"{parent_role_name}_{forest_client_number}"


def construct_forest_client_role_purpose(
    parent_role_purpose: str, forest_client_number: str
):
    LOGGER.debug(f"parent_role_purpose: {parent_role_purpose}")
    client_purpose = f"{parent_role_purpose} for {forest_client_number}"
    return client_purpose


def find_or_create_forest_client_child_role(
    db: Session, forest_client_number: str, parent_role: models.FamRole, requester: str
):
    # Note, client_name is unique. For now for MVP version we will insert it with
    # a dummy name.
    # client_name = f"{famConstants.DUMMY_FOREST_CLIENT_NAME}_{forest_client_number}"

    # Note, this is current implementation for fam_forest_client as to programmatically
    # insert a record into the table. Later FAM will be interfacing with Forest
    # Client API, thus the way to insert a record will cahnge.
    forest_client = crud_forest_client.find_or_create(  # NOSONAR
        db, forest_client_number, requester
    )
    LOGGER.debug(f"forest client number from db: {forest_client.forest_client_number}")
    LOGGER.debug(f"forest client client id from db: {forest_client.client_number_id}")

    forest_client_role_name = construct_forest_client_role_name(
        parent_role.role_name, forest_client_number
    )
    # Verify if Forest Client role (child role) exist
    child_role = crud_role.get_role_by_role_name_and_app_id(
        db, forest_client_role_name, parent_role.application_id
    )
    LOGGER.debug(
        "Forest Client child role for role_name "
        f"'{forest_client_role_name}':"
        f" {'Does not exist' if not child_role else 'Exists'}"
    )

    if not child_role:
        child_role = crud_role.create_role(
            schemas.FamRoleCreate(
                **{
                    "parent_role_id": parent_role.role_id,
                    "application_id": parent_role.application_id,
                    "forest_client_number": forest_client_number,
                    "role_name": forest_client_role_name,
                    "role_purpose": construct_forest_client_role_purpose(
                        parent_role_purpose=parent_role.role_purpose,
                        forest_client_number=forest_client_number,
                    ),
                    "create_user": requester,
                    "role_type_code": famConstants.RoleType.ROLE_TYPE_CONCRETE,
                }
            ),
            db,
        )
        LOGGER.debug(
            f"Child role {child_role.role_id} added for parent role "
            f"{parent_role.role_name}({child_role.parent_role_id})."
        )
    return child_role


def find_by_id(db: Session, user_role_xref_id: int) -> models.FamUserRoleXref:
    user_role = (
        db.query(models.FamUserRoleXref)
        .filter(models.FamUserRoleXref.user_role_xref_id == user_role_xref_id)
        .one_or_none()
    )
    return user_role
