import logging
from http import HTTPStatus

from api.app.crud import crud_role, crud_user, crud_user_role
from api.app.models import model as models
from api.app.routers.router_guards import (authorize_by_application_role,
                                           get_current_requester)
from api.app.schemas import Requester
from api.app.utils.audit_util import (AuditEventLog, AuditEventOutcome,
                                      AuditEventType)
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from .. import database, jwt_validation, schemas

LOGGER = logging.getLogger(__name__)

ERROR_SELF_GRANT_PROHIBITED = "self_grant_prohibited"

router = APIRouter()


@router.post("",
    response_model=schemas.FamUserRoleAssignmentGet,
    dependencies=[Depends(authorize_by_application_role)]
)
def create_user_role_assignment(
    role_assignment_request: schemas.FamUserRoleAssignmentCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize),
    requester: Requester = Depends(get_current_requester)
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
        event_outcome=AuditEventOutcome.SUCCESS
    )

    # TODO migrate to @audit_log(??),
    # TODO how to handle exception in audit_log,
    # TODO verify how exception_handler react to error.
    try:

        requesting_user = get_requesting_user(db, requester.cognito_user_id) # TODO See if can use Requester to convert instead.
        role = crud_role.get_role(db, role_assignment_request.role_id)

        # TODO Why we need to query this when user has role (shouldn't be queried for audit I think).
        audit_event_log.role = role
        audit_event_log.application = role.application # TODO: later router is validate with authorized_by_app_id, I think that should be first.
        audit_event_log.requesting_user = requesting_user

        # TODO: use depends
        enforce_self_grant_guard_properties(
            db,
            requesting_user,
            role_assignment_request.user_type_code,
            role_assignment_request.user_name,
        )

        return crud_user_role.create_user_role(
            db, role_assignment_request, requesting_user.cognito_user_id
        )

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        audit_event_log.target_user = crud_user.get_user_by_domain_and_name(
            db,
            role_assignment_request.user_type_code,
            role_assignment_request.user_name
        )
        if audit_event_log.target_user is None:
            audit_event_log.target_user = models.FamUser(
                user_type_code=role_assignment_request.user_type_code,
                user_name=role_assignment_request.user_name,
                user_guid="unknown",
                cognito_user_id="unknown"
            )

        audit_event_log.log_event()


@router.delete(
    "/{user_role_xref_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(authorize_by_application_role)]
)
def delete_user_role_assignment(
    request: Request,
    user_role_xref_id: int,
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester)
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
        event_type=AuditEventType.CREATE_USER_ROLE_ACCESS,
        event_outcome=AuditEventOutcome.SUCCESS
    )

    try:
        requesting_user = get_requesting_user(db, requester.cognito_user_id)
        user_role = crud_user_role.find_by_id(db, user_role_xref_id)

        audit_event_log.role = user_role.role
        audit_event_log.target_user = user_role.user
        audit_event_log.application = user_role.role.application
        audit_event_log.requesting_user = requesting_user

        # Enforce self-grant guard
        enforce_self_grant_guard_objects(
            db,
            requesting_user,
            user_role.user,
        )

        crud_user_role.delete_fam_user_role_assignment(db, user_role_xref_id)

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        if user_role.role.client_number:
            audit_event_log.forest_client_number = user_role.role.client_number.forest_client_number
        audit_event_log.log_event()


def enforce_self_grant_guard_properties(
    db: Session,
    requesting_user: models.FamUser,
    target_user_type_code,
    target_user_user_name,
):
    target_user = crud_user.get_user_by_domain_and_name(
        db,
        target_user_type_code,
        target_user_user_name,
    )
    return enforce_self_grant_guard_objects(db, requesting_user, target_user)


def enforce_self_grant_guard_objects(
    db: Session,
    requesting_user: models.FamUser,
    target_user: models.FamUser,
):
    if target_user is not None:
        is_same_user_name = requesting_user.user_name == target_user.user_name
        is_same_user_type_code = (
            requesting_user.user_type_code == target_user.user_type_code
        )

        if is_same_user_name and is_same_user_type_code:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": ERROR_SELF_GRANT_PROHIBITED,
                    "description": "Granting roles to self is not allowed",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )


def get_requesting_user(db: Session, cognito_user_id: str) -> models.FamUser:

    requester = crud_user.get_user_by_cognito_user_id(db, cognito_user_id)
    return requester
