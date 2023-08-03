from http import HTTPStatus
import logging

from pydantic import BaseModel

from api.app.crud import crud_user_role, crud_application, crud_user
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.orm import Session

from api.requester import Requester, get_current_requester
from api.app.utils.audit_util import AuditEvent, AuditEventOutcome, AuditEventOutcome, audit_log

from .. import database, schemas, jwt_validation

LOGGER = logging.getLogger(__name__)

ERROR_SELF_GRANT_PROHIBITED = "self_grant_prohibited"

router = APIRouter()


@router.post("", response_model=schemas.FamUserRoleAssignmentGet)
def create_user_role_assignment(
    role_assignment_request: schemas.FamUserRoleAssignmentCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize),
    requestor: Requester = Depends(get_current_requester)
):
    """
    Create FAM user_role_xref association.
    """
    LOGGER.debug(f"Executing 'create_user_role_assignment' "\
                 f"with request: {role_assignment_request}, requestor: {requestor}")
    # Enforce application-level security
    application_id = crud_application.get_application_id_by_role_id(
        db, role_assignment_request.role_id
    )
    jwt_validation.authorize_by_app_id(application_id, db, token_claims)

    # Enforce self-grant guard
    request_user_name = role_assignment_request.user_name
    request_user_type_code = role_assignment_request.user_type_code
    enforce_self_grant_guard(db, requestor.cognito_user_id, request_user_name, request_user_type_code)

    try:
        create_data = crud_user_role.create_user_role(
            db, role_assignment_request, requestor.cognito_user_id
        )
        LOGGER.debug(
            "User/Role assignment executed successfully, "
            f"id: {create_data.user_role_xref_id}"
        )

        # audit log for success
        audit_log(
            request=request,
            event=AuditEvent.CREATE_USER_ROLE_ACCESS,
            requestor=requestor,
            target=to_audit_target(role_assignment_request)
            outcome=AuditEventOutcome.SUCCESS
        )
        return create_data

    except Exception as e:

        # audit log for fail
        audit_log(
            request=request,
            event=AuditEvent.CREATE_USER_ROLE_ACCESS,
            requestor=requestor,
            outcome=AuditEventOutcome.FAIL
        )
        raise e



@router.delete(
    "/{user_role_xref_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(jwt_validation.get_request_cognito_user_id)],
)
def delete_user_role_assignment(
    user_role_xref_id: int,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize),
    cognito_user_id: str = Depends(jwt_validation.get_request_cognito_user_id),
) -> None:
    """
    Delete FAM user_role_xref association.
    """
    """
    Note! There appear to be a bug in FasAPI/Starlette, when http status 204 No-Content is returned (like Delete)
    but, for some reason response still has content and throw error.
    To fix: see this => https://lightrun.com/answers/tiangolo-fastapi-response-content-longer-than-content-length-error-for-delete-and-nocontent
    (response_class=Response) is added to @router.delete with 204 status.
    """

    # Enforce application-level security
    application_id = crud_application.get_application_id_by_user_role_xref_id(
        db, user_role_xref_id
    )
    jwt_validation.authorize_by_app_id(application_id, db, token_claims)

    # Enforce self-grant guard
    target_user = crud_user.get_user_by_user_role_xref_id(db, user_role_xref_id)
    enforce_self_grant_guard(db, cognito_user_id, target_user.user_name, target_user.user_type_code)

    crud_user_role.delete_fam_user_role_assignment(db, user_role_xref_id)
    LOGGER.debug(f"User/Role assignment deleted successfully, id: {user_role_xref_id}")


def enforce_self_grant_guard(db, requester, target_user_name, target_user_type_code):
    requesting_user = crud_user.get_user_by_cognito_user_id(db, requester)
    if requesting_user is not None:
        is_same_user_name = requesting_user.user_name == target_user_name
        is_same_user_type_code = requesting_user.user_type_code == target_user_type_code

        if is_same_user_name and is_same_user_type_code:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": ERROR_SELF_GRANT_PROHIBITED,
                    "description": "Granting roles to self is not allowed",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

def to_audit_target(target_param):
    pass