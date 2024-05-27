import logging
from http import HTTPStatus
from typing import Optional

from api.app import constants as famConstants, schemas
from api.app.crud import crud_forest_client, crud_role, crud_user
from api.app.models import model as models
from api.app.integration.forest_client.forest_client import ForestClientService
from api.app.utils.utils import raise_http_exception
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


def create_user_role(
    db: Session,
    request: schemas.FamUserRoleAssignmentCreate,
    requester: str,
    target_user_business_guid: Optional[str] = None
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
            error_msg=error_msg
        )

    # Determine if user already exists or add a new user.
    fam_user = crud_user.find_or_create(
        db,
        request.user_type_code,
        request.user_name,
        request.user_guid,
        requester
    )
    fam_user = crud_user.update_user_business_guid(
        db, fam_user.user_id, target_user_business_guid, requester
    )

    # Verify if role exists.
    fam_role = crud_role.get_role(db, request.role_id)
    if not fam_role:
        error_msg = f"Role id {request.role_id} does not exist."
        raise_http_exception(
            error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
            error_msg=error_msg
        )

    LOGGER.debug(
        f"Role for user_role assignment found: {fam_role.role_name}" +
        f"({fam_role.role_id})."
    )

    # Role is a 'Concrete' type, then create role assignment directly with the role.
    # Role is a 'Abstract' type, create role assignment with forst client child role.
    require_child_role = (
        fam_role.role_type_code == famConstants.RoleType.ROLE_TYPE_ABSTRACT
    )

    if require_child_role:
        LOGGER.debug(
            f"Role {fam_role.role_name} requires child role "
            "for user/role assignment."
        )

        if (not hasattr(request, "forest_client_number")
                or request.forest_client_number is None):
            error_msg = (
                "Invalid role assignment request. Cannot assign user " +
                f"{request.user_name} to abstract role {fam_role.role_name}")
            raise_http_exception(
                error_code=famConstants.ERROR_CODE_MISSING_KEY_ATTRIBUTE,
                error_msg=error_msg
            )

        validator = UserRoleValidator(request)
        if (not validator.forest_client_number_exists()):
            error_msg = (
                "Invalid role assignment request. " +
                f"Forest Client Number {request.forest_client_number} does not exist.")
            raise_http_exception(
                error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                error_msg=error_msg
            )

        if (not validator.forest_client_active()):
            error_msg = (
                "Invalid role assignment request. Forest Client is not in Active status: " +
                f"{validator.get_forest_client()[famConstants.FOREST_CLIENT_STATUS['KEY']]}")
            raise_http_exception(
                error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                error_msg=error_msg
            )

        # Note: current FSA design in the 'request body' contains a
        #     'forest_client_number' if it requires a child role.
        child_role = find_or_create_forest_client_child_role(
            db,
            request.forest_client_number,
            fam_role,
            requester
        )

    # Role Id for associating with user
    associate_role_id = child_role.role_id if require_child_role else fam_role.role_id

    # Create user/role assignment.
    fam_user_role_xref = get_use_role_by_user_id_and_role_id(db, fam_user.user_id, associate_role_id)

    if fam_user_role_xref:
        LOGGER.debug(
            "FamUserRoleXref already exists with id: " +
            f"{fam_user_role_xref.user_role_xref_id}."
        )

        error_msg = "Role already assigned to user."
        raise_http_exception(
            status_code=HTTPStatus.CONFLICT,
            error_msg=error_msg
        )
    else:
        fam_user_role_xref = create(db, fam_user.user_id, associate_role_id, requester)

    xref_dict = fam_user_role_xref.__dict__
    xref_dict["application_id"] = (
        child_role.application_id if require_child_role else fam_role.application_id
    )
    user_role_assignment = schemas.FamUserRoleAssignmentGet(**xref_dict)
    LOGGER.debug(f"User/Role assignment executed successfully: {user_role_assignment}")
    return user_role_assignment


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
        f"FamUserRoleXref - 'create' with user_id: {user_id}, " +
        f"role_id: {role_id}."
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
    LOGGER.debug(f'forest client number from db: {forest_client.forest_client_number}')
    LOGGER.debug(f'forest client client id from db: {forest_client.client_number_id}')

    forest_client_role_name = construct_forest_client_role_name(
        parent_role.role_name, forest_client_number
    )
    # Verify if Forest Client role (child role) exist
    child_role = crud_role.get_role_by_role_name_and_app_id(
        db,
        forest_client_role_name,
        parent_role.application_id
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
                        forest_client_number=forest_client_number
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


def find_by_id(
    db: Session, user_role_xref_id: int
) -> models.FamUserRoleXref:
    user_role = (
        db.query(models.FamUserRoleXref)
        .filter(
            models.FamUserRoleXref.user_role_xref_id == user_role_xref_id
        )
        .one_or_none()
    )
    return user_role


class UserRoleValidator:
    """
    Purpose: More validations on inputs (other than basic validations) and
             business rules validations (if any).
    Cautious: Do not instantiate the class for more than one time per request.
              It calls Forest Client API remotely if needs to.
    """
    LOGGER = logging.getLogger(__name__)

    def __init__(self, request: schemas.FamUserRoleAssignmentCreate):
        LOGGER.debug(f"Validator '{self.__class__.__name__}' with input '{request}'.")

        self.user_role_request = request
        # Note - this value should already be validated from schema input validation.
        forest_client_number = request.forest_client_number
        if forest_client_number is not None:
            fc_api = ForestClientService()

            # Locally stored (if any) for later use to prevent api calls again.
            # Exact client number search - should only contain 1 result.
            self.fc = fc_api.find_by_client_number(forest_client_number)
            LOGGER.debug(f"Forest Client(s) retrieved: {self.fc}")

    def forest_client_number_exists(self) -> bool:
        # Exact client number search - should only contain 1 result.
        return len(self.fc) == 1

    def forest_client_active(self) -> bool:
        return (
            (self.get_forest_client()[famConstants.FOREST_CLIENT_STATUS["KEY"]]
                == famConstants.FOREST_CLIENT_STATUS["CODE_ACTIVE"])
            if self.forest_client_number_exists()
            else False
        )

    def get_forest_client(self):
        return self.fc[0] if self.forest_client_number_exists() else None
