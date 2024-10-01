import logging
from http import HTTPStatus
from typing import List

from api.app import constants as famConstants
from api.app.crud import crud_forest_client, crud_role, crud_user, crud_utils
from api.app.crud.services.permission_audit_service import \
    PermissionAuditService
from api.app.crud.validator.forest_client_validator import (
    forest_client_active, forest_client_number_exists,
    get_forest_client_status)
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.integration.gc_notify import GCNotifyEmailService
from api.app.models import model as models
from api.app.schemas import (FamApplicationUserRoleAssignmentGetSchema,
                             FamRoleCreateSchema,
                             FamUserRoleAssignmentCreateRes,
                             FamUserRoleAssignmentCreateSchema,
                             GCNotifyGrantAccessEmailParamSchema,
                             TargetUserSchema)
from api.app.schemas.fam_forest_client import FamForestClientSchema
from api.app.schemas.requester import RequesterSchema
from api.app.utils.utils import raise_http_exception
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


def create_user_role_assignment_many(
    db: Session,
    request: FamUserRoleAssignmentCreateSchema,
    target_user: TargetUserSchema,
    requester: RequesterSchema,
) -> List[FamUserRoleAssignmentCreateRes]:
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
        db, request.user_type_code, request.user_name, request.user_guid, requester.cognito_user_id
    )
    fam_user = crud_user.update_user_properties_from_verified_target_user(
        db, fam_user.user_id, target_user, requester.cognito_user_id,
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

    new_user_permission_granted_list: List[FamUserRoleAssignmentCreateRes] = []

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
        forest_client_integration_service = ForestClientIntegrationService(api_instance_env)

        for forest_client_number in request.forest_client_numbers:
            # validate the forest client number
            forest_client_search_return = (
                forest_client_integration_service.find_by_client_number(
                    forest_client_number
                )
            )

            if not forest_client_number_exists(forest_client_search_return):
                error_msg = (
                    "Invalid role assignment request. "
                    + f"Forest Client Number {forest_client_number} does not exist."
                )
                raise_http_exception(
                    error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                    error_msg=error_msg,
                )

            if not forest_client_active(forest_client_search_return):
                error_msg = (
                    f"Invalid role assignment request. Forest client number {forest_client_number} is not in active status:"
                    + f"{get_forest_client_status(forest_client_search_return)}"
                )
                raise_http_exception(
                    error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                    error_msg=error_msg,
                )

            # Check if child role exists or add a new child role
            child_role = find_or_create_forest_client_child_role(
                db, forest_client_number, fam_role, requester.cognito_user_id,
            )
            # Create user/role assignment
            new_user_role_assginment_res = create_user_role_assignment(
                db, fam_user, child_role, requester.cognito_user_id,
            )

            # Update response object for Forest Client Name from the forest_client_search.
            # FAM currently does not store forest client name for easy retrieval.
            new_user_role_assginment_res.detail.role.forest_client = FamForestClientSchema.from_api_json(forest_client_search_return[0])
            new_user_permission_granted_list.append(new_user_role_assginment_res)
    else:
        # Create user/role assignment
        new_user_role_assginment_res = create_user_role_assignment(
            db, fam_user, fam_role, requester.cognito_user_id,
        )
        new_user_permission_granted_list.append(new_user_role_assginment_res)
    LOGGER.info(f"User/Role assignment executed successfully: {new_user_permission_granted_list}")

    permission_audit_service = PermissionAuditService(db)
    permission_audit_service.store_user_permissions_granted_audit_history(
        requester, fam_user, new_user_permission_granted_list
    )

    return new_user_permission_granted_list


def create_user_role_assignment(
    db: Session, user: models.FamUser, role: models.FamRole, requester_cognito_user_id: str
):
    new_user_role_assginment_res = None
    fam_user_role_xref = get_use_role_by_user_id_and_role_id(
        db, user.user_id, role.role_id
    )

    if fam_user_role_xref:
        error_msg = f"Role {fam_user_role_xref.role.role_name} already assigned to user {fam_user_role_xref.user.user_name}."
        new_user_role_assginment_res = FamUserRoleAssignmentCreateRes(
            **{
                "status_code": HTTPStatus.CONFLICT,
                "detail": FamApplicationUserRoleAssignmentGetSchema(
                    **fam_user_role_xref.__dict__
                ),
                "error_message": error_msg,
            }
        )
    else:
        fam_user_role_xref = create(db, user.user_id, role.role_id, requester_cognito_user_id)
        new_user_role_assginment_res = FamUserRoleAssignmentCreateRes(
            **{
                "status_code": HTTPStatus.OK,
                "detail": FamApplicationUserRoleAssignmentGetSchema(
                    **fam_user_role_xref.__dict__
                ),
            }
        )

    return new_user_role_assginment_res


def delete_fam_user_role_assignment(db: Session, requester: RequesterSchema, user_role_xref_id: int):
    record = (
        db.query(models.FamUserRoleXref)
        .filter(models.FamUserRoleXref.user_role_xref_id == user_role_xref_id)
        .one()
    )

    # save audit record
    permission_audit_service = PermissionAuditService(db)
    permission_audit_service.store_user_permissions_revoked_audit_history(
        requester, record
    )

    db.delete(record)
    db.flush()


def create(db: Session, user_id: int, role_id: int, requester_cognito_user_id: str):
    LOGGER.debug(
        f"FamUserRoleXref - 'create' with user_id: {user_id}, " + f"role_id: {role_id}."
    )

    new_fam_user_role: models.FamUserRoleXref = models.FamUserRoleXref(
        **{
            "user_id": user_id,
            "role_id": role_id,
            "create_user": requester_cognito_user_id,
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
    db: Session, forest_client_number: str, parent_role: models.FamRole, requester_cognito_user_id: str
):
    # Note, client_name is unique. For now for MVP version we will insert it with
    # a dummy name.
    # client_name = f"{famConstants.DUMMY_FOREST_CLIENT_NAME}_{forest_client_number}"

    # Note, this is current implementation for fam_forest_client as to programmatically
    # insert a record into the table. Later FAM will be interfacing with Forest
    # Client API, thus the way to insert a record will cahnge.
    forest_client = crud_forest_client.find_or_create(  # NOSONAR
        db, forest_client_number, requester_cognito_user_id
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
            FamRoleCreateSchema(
                **{
                    "parent_role_id": parent_role.role_id,
                    "application_id": parent_role.application_id,
                    "forest_client_number": forest_client_number,
                    "role_name": forest_client_role_name,
                    "display_name": parent_role.display_name,
                    "role_purpose": construct_forest_client_role_purpose(
                        parent_role_purpose=parent_role.role_purpose,
                        forest_client_number=forest_client_number,
                    ),
                    "create_user": requester_cognito_user_id,
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


def send_user_access_granted_email(
    target_user: TargetUserSchema,
    roles_assignment_responses: List[FamUserRoleAssignmentCreateRes],
):
    """
    Send email using GC Notify integration service.
    TODO: Erro handling when sending email encountered technical errors (400/500). Ticket #1471.
        - do not fail event when sending email fails (400/500).
        - 'create_user_role_assignment_many' router's response schema needs to be refactored.
        - if email sent -> include in response status/message email is sent.
        - if email sent failed (400/500) -> include in response status/message email is not sent
        - frontend needs to display email sent failure message.

    Note
        - FAM currently is not concerned with checking status from GC Notify (callback) to verify
            if email is really sent from GC Notify.
    """
    granted_roles = list(filter(
        lambda res: res.status_code == HTTPStatus.OK,
        roles_assignment_responses
    ))
    if len(granted_roles) == 0:  # no role is granted, no email needs to be sent.
        return

    email_params: GCNotifyGrantAccessEmailParamSchema = None
    try:
        granted_role = granted_roles[0].detail.role
        is_forest_client_scoped_role = granted_role.forest_client is not None
        granted_role_client_list = (
            list(map(lambda item: item.detail.role.forest_client, roles_assignment_responses))
            if is_forest_client_scoped_role
            else None
        )
        email_service = GCNotifyEmailService()
        email_params = GCNotifyGrantAccessEmailParamSchema(
            **{
                "user_name": target_user.user_name,
                "first_name": target_user.first_name,
                "last_name": target_user.last_name,
                "application_description": granted_role.application.application_description,
                "role_display_name": granted_role.display_name,
                "organization_list": granted_role_client_list,
                "application_team_contact_email": None,  # TODO: ticket #1507 to implement this.
                "send_to_email": target_user.email,
            }
        )

        email_service.send_user_access_granted_email(email_params)
        LOGGER.debug(f"Email is sent to {email_params.send_to_email}.")
        return famConstants.EmailSendingStatus.SENT_TO_EMAIL_SERVICE_SUCCESS

    except Exception as e:
        LOGGER.warning(f"Failure sending email to {email_params.send_to_email}.")
        LOGGER.debug(f"Failure reason: {e}.")
        return famConstants.EmailSendingStatus.SENT_TO_EMAIL_SERVICE_FAILURE
