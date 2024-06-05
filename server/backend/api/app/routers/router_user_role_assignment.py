import logging
from http import HTTPStatus

from api.app.crud import crud_role, crud_user, crud_user_role
from api.app.models import model as models
from api.app.routers.router_guards import (
    authorize_by_application_role,
    authorize_by_privilege,
    authorize_by_user_type,
    enforce_self_grant_guard,
    enforce_bceid_by_same_org_guard,
    get_current_requester,
    get_verified_target_user,
)
from api.app.schemas import Requester, TargetUser
from api.app.utils.audit_util import AuditEventLog, AuditEventOutcome, AuditEventType
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from .. import database, jwt_validation, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=schemas.FamUserRoleAssignmentGet,
    # Guarding endpoint with Depends().
    dependencies=[
        Depends(enforce_self_grant_guard),
        Depends(
            authorize_by_application_role
        ),  # requester needs to be app admin or delegated admin
        Depends(
            authorize_by_privilege
        ),  # if requester is delegated admin, needs to have privilge to grant access with the request role
        Depends(
            authorize_by_user_type
        ),  # check business bceid user cannot grant idir user access
        Depends(
            enforce_bceid_by_same_org_guard
        ),  # check business bceid user can only grant access for the user from same organization
    ],
)
def create_user_role_assignment(
    role_assignment_request: schemas.FamUserRoleAssignmentCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.validate_token),
    requester: Requester = Depends(get_current_requester),
    target_user: TargetUser = Depends(get_verified_target_user),
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
        forest_client_number=role_assignment_request.forest_client_number,
        event_outcome=AuditEventOutcome.SUCCESS,
    )

    try:

        requesting_user = get_requesting_user(db, requester.cognito_user_id)
        role = crud_role.get_role(db, role_assignment_request.role_id)

        audit_event_log.role = role
        audit_event_log.application = role.application
        audit_event_log.requesting_user = requesting_user

        return crud_user_role.create_user_role(
            db,
            role_assignment_request,
            requesting_user.cognito_user_id,
            target_user.business_guid,
        )

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        audit_event_log.target_user = crud_user.get_user_by_domain_and_name(
            db,
            role_assignment_request.user_type_code,
            role_assignment_request.user_name,
        )
        if audit_event_log.target_user is None:
            audit_event_log.target_user = models.FamUser(
                user_type_code=role_assignment_request.user_type_code,
                user_name=role_assignment_request.user_name,
                user_guid="unknown",
                cognito_user_id="unknown",
            )

        audit_event_log.log_event()


@router.delete(
    "/{user_role_xref_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_class=Response,
    dependencies=[
        Depends(enforce_self_grant_guard),
        Depends(authorize_by_application_role),
        Depends(authorize_by_privilege),
        Depends(authorize_by_user_type),
        Depends(enforce_bceid_by_same_org_guard),
    ],
)
def delete_user_role_assignment(
    request: Request,
    user_role_xref_id: int,
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
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
        requesting_user = get_requesting_user(db, requester.cognito_user_id)
        user_role = crud_user_role.find_by_id(db, user_role_xref_id)

        audit_event_log.role = user_role.role
        audit_event_log.target_user = user_role.user
        audit_event_log.application = user_role.role.application
        audit_event_log.requesting_user = requesting_user

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


def get_requesting_user(db: Session, cognito_user_id: str) -> models.FamUser:
    requester = crud_user.get_user_by_cognito_user_id(db, cognito_user_id)
    return requester
