import logging
from http import HTTPStatus

from api.app.crud import crud_role, crud_user, crud_user_role
from api.app.models.model import FamUser
from api.app.routers.router_guards import (
    authorize_by_application_role,
    authorize_by_privilege,
    authorize_by_user_type,
    enforce_bceid_by_same_org_guard,
    enforce_bceid_terms_conditions_guard,
    enforce_self_grant_guard,
    get_current_requester,
    get_verified_target_user,
)
from api.app.schemas import (
    FamUserRoleAssignmentCreateSchema,
    FamUserRoleAssignmentResponseSchema,
    RequesterSchema,
    TargetUserSchema,
)
from api.app.utils.audit_util import AuditEventLog, AuditEventOutcome, AuditEventType
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from .. import database, jwt_validation

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=FamUserRoleAssignmentResponseSchema,
    # Guarding endpoint with Depends().
    dependencies=[
        Depends(enforce_self_grant_guard),
        Depends(enforce_bceid_terms_conditions_guard),
        Depends(
            authorize_by_application_role
        ),  # Requester needs to be app admin or delegated admin
        Depends(
            authorize_by_privilege
        ),  # if Requester is delegated admin, needs to have privilge to grant access with the request role
        Depends(
            authorize_by_user_type
        ),  # check business bceid user cannot grant idir user access
        Depends(
            enforce_bceid_by_same_org_guard
        ),  # check business bceid user can only grant access for the user from same organization
    ],
    description="Grant User Access to an application's role.",
)
def create_user_role_assignment_many(
    role_assignment_request: FamUserRoleAssignmentCreateSchema,
    request: Request,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.validate_token),
    requester: RequesterSchema = Depends(get_current_requester),
    target_user: TargetUserSchema = Depends(get_verified_target_user),
):
    """
    Create FAM user_role_xref association.
    """
    LOGGER.debug(
        f"Executing 'create_user_role_assignment' "
        f"with request: {role_assignment_request}, requestor: {token_claims}"
    )

    audit_event_log = AuditEventLog(
        request=request,
        event_type=AuditEventType.CREATE_USER_ROLE_ACCESS,
        forest_client_numbers=role_assignment_request.forest_client_numbers,
        event_outcome=AuditEventOutcome.SUCCESS,
    )

    try:
        role = crud_role.get_role(db, role_assignment_request.role_id)

        audit_event_log.role = role
        audit_event_log.application = role.application
        audit_event_log.requesting_user = requester

        response = FamUserRoleAssignmentResponseSchema(
            assignments_detail=crud_user_role.create_user_role_assignment_many(
                db,
                role_assignment_request,
                target_user,
                requester.cognito_user_id,
            )
        )

        # get target user from database, so for existing user, we can get the cognito user id
        audit_event_log.target_user = crud_user.get_user_by_domain_and_guid(
            db,
            role_assignment_request.user_type_code,
            role_assignment_request.user_guid,
        )

        # sending user notification after event is finished.
        if role_assignment_request.requires_send_user_email:
            response.email_sending_status = crud_user_role.send_user_access_granted_email(
                target_user=target_user,
                roles_assignment_responses=response.assignments_detail
            )

        return response

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e

        raise e

    finally:
        # if failed to get target user from database, use the information from request
        if audit_event_log.target_user is None:
            audit_event_log.target_user = FamUser(
                user_type_code=target_user.user_type_code,
                user_name=target_user.user_name,
                user_guid=target_user.user_guid,
                cognito_user_id=target_user.cognito_user_id,
            )
        audit_event_log.log_event()


@router.delete(
    "/{user_role_xref_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_class=Response,
    dependencies=[
        Depends(enforce_self_grant_guard),
        Depends(enforce_bceid_terms_conditions_guard),
        Depends(authorize_by_application_role),
        Depends(authorize_by_privilege),
        Depends(authorize_by_user_type),
        Depends(enforce_bceid_by_same_org_guard),
    ],
    description="Remove a specific application's role from user's access.",
)
def delete_user_role_assignment(
    request: Request,
    user_role_xref_id: int,
    db: Session = Depends(database.get_db),
    requester: RequesterSchema = Depends(get_current_requester),
) -> None:
    """
    Delete FAM user_role_xref association.
    """
    """
    Note! There appear to be a bug in FasAPI/Starlette, when http status 204
    No-Content is returned (like Delete) but, for some reason response still has
    content and throw error.
    To fix: see this =>
    https://lightrun.com/answers/tiangolo-fastapi-response-content-longer-than-content-length-error-for-delete-and-nocontent
    (response_class=Response) is added to @router.delete with 204 status.
    """

    audit_event_log = AuditEventLog(
        request=request,
        event_type=AuditEventType.REMOVE_USER_ROLE_ACCESS,
        event_outcome=AuditEventOutcome.SUCCESS,
    )

    try:
        user_role = crud_user_role.find_by_id(db, user_role_xref_id)

        audit_event_log.role = user_role.role
        audit_event_log.target_user = user_role.user
        audit_event_log.application = user_role.role.application
        audit_event_log.requesting_user = requester

        crud_user_role.delete_fam_user_role_assignment(db, user_role_xref_id)

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        if user_role.role.client_number:
            audit_event_log.forest_client_number = (
                user_role.role.client_number.forest_client_number
            )
        audit_event_log.log_event()
