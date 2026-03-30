import logging
from http import HTTPStatus

from api.app.crud import crud_role, crud_user_role
from api.app.routers.router_guards import (
    authorize_by_application_role, authorize_by_privilege,
    authorize_by_user_type, enforce_bceid_by_same_org_guard,
    enforce_bceid_terms_conditions_guard, enforce_self_grant_guard,
    get_current_requester, get_verified_target_users)
from api.app.schemas import (FamUserRoleAssignmentCreateSchema,
                             FamUserRoleAssignmentRes, RequesterSchema)
from api.app.schemas.fam_user_role_assignment_create_response import FamUserRoleAssignmentCreateRes
from api.app.schemas.target_user_validation_result import TargetUserValidationResultSchema
from api.app.utils.audit_util import (AuditEventLog, AuditEventOutcome,
                                      AuditEventType)
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from .. import database, jwt_validation
from api.app.crud.crud_user_role import send_users_access_granted_emails

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=FamUserRoleAssignmentRes,
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
        )  # check business bceid user cannot grant idir user access
    ],
    summary="Grant multiple users access to an application's role.",
    description="Granting IDIR/BCeID users access to an application's role, supporting expiry dates for role assignments.",
)
def create_user_role_assignment_many(
    role_assignment_request: FamUserRoleAssignmentCreateSchema,
    request: Request,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.enforce_fam_client_token),
    requester: RequesterSchema = Depends(get_current_requester),
    target_users: TargetUserValidationResultSchema = Depends(get_verified_target_users),
):
    """
    Create FAM user_role_xref associations for multiple users.
    """
    LOGGER.debug(
        f"Executing 'create_user_role_assignment' "
        f"with request: {role_assignment_request}, requestor: {token_claims}"
    )

    audit_event_log = AuditEventLog(
        request=request,
        event_type=AuditEventType.CREATE_USER_ROLE_ACCESS,
        forest_client_numbers=role_assignment_request.forest_client_numbers,
        role_assignment_expiry_date=role_assignment_request.expiry_date_date,
        event_outcome=AuditEventOutcome.SUCCESS
    )

    try:
        role = crud_role.get_role(db, role_assignment_request.role_id)

        audit_event_log.role = role
        audit_event_log.application = role.application
        audit_event_log.requesting_user = requester

        # Grant access for all verified users (may still fail due to other business rules)
        assignments_results = crud_user_role.create_user_role_assignment_many(
            db,
            role_assignment_request,
            target_users.verified_users,
            requester,
        )

        response = FamUserRoleAssignmentRes(
            assignments_detail=assignments_results +
            # Failed assignments for users that did not pass IDIM validation
            [
                FamUserRoleAssignmentCreateRes(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=None,
                    error_message=getattr(failed_user, "error_reason", "User identification validation failed"),
                )
                for failed_user in target_users.failed_users
            ]
        )

        audit_event_log.user_assignment_results = response.assignments_detail

        # sending user notification after event is finished (for all verified users)
        if role_assignment_request.requires_send_user_email:
            send_users_access_granted_emails(target_users.verified_users, assignments_results)

        return response

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        # No longer set a single target_user; batch context
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
        expiry = user_role.expiry_date
        audit_event_log.role_assignment_expiry_date = expiry.isoformat() if expiry else None

        crud_user_role.delete_fam_user_role_assignment(db, requester, user_role_xref_id)

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        if user_role.role.forest_client_relation:
            audit_event_log.forest_client_number = (
                user_role.role.forest_client_relation.forest_client_number
            )
        audit_event_log.log_event()
