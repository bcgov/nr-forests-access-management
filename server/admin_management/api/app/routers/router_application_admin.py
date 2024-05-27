import logging
from typing import List

from api.app import database, jwt_validation, schemas
from api.app.models import model as models
from api.app.routers.router_guards import (
    authorize_by_fam_admin,
    enforce_self_grant_guard,
    get_current_requester,
    get_verified_target_user,
    validate_param_application_admin_id,
    validate_param_application_id,
    validate_param_user_type,
)
from api.app.routers.router_utils import (
    application_admin_service_instance,
    application_service_instance,
    user_service_instance,
)
from api.app.schemas import Requester, TargetUser
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.application_service import ApplicationService
from api.app.services.user_service import UserService
from api.app.utils.audit_util import AuditEventLog, AuditEventOutcome, AuditEventType
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=List[schemas.FamAppAdminGetResponse],
    status_code=200,
    dependencies=[Depends(authorize_by_fam_admin)],
)
async def get_application_admins(
    application_admin_service: ApplicationAdminService = Depends(
        application_admin_service_instance
    ),
):
    return application_admin_service.get_application_admins()


@router.post(
    "",
    response_model=schemas.FamAppAdminGetResponse,
    dependencies=[
        Depends(authorize_by_fam_admin),
        Depends(enforce_self_grant_guard),
        Depends(validate_param_application_id),
        Depends(validate_param_user_type),
    ],
)
def create_application_admin(
    application_admin_request: schemas.FamAppAdminCreateRequest,
    request: Request,
    token_claims: dict = Depends(jwt_validation.authorize),
    requester: Requester = Depends(get_current_requester),
    target_user: TargetUser = Depends(get_verified_target_user),  # validate target user
    application_admin_service: ApplicationAdminService = Depends(
        application_admin_service_instance
    ),
    application_service: ApplicationService = Depends(application_service_instance),
    user_service: UserService = Depends(user_service_instance),
):
    LOGGER.debug(
        f"Executing 'create_application_admin' "
        f"with request: {application_admin_request}, requestor: {token_claims}"
    )

    audit_event_log = AuditEventLog(
        request=request,
        event_type=AuditEventType.CREATE_APPLICATION_ADMIN_ACCESS,
        event_outcome=AuditEventOutcome.SUCCESS,
    )

    try:
        audit_event_log.requesting_user = user_service.get_user_by_cognito_user_id(
            requester.cognito_user_id
        )
        audit_event_log.application = application_service.get_application(
            application_admin_request.application_id
        )

        return application_admin_service.create_application_admin(
            application_admin_request, requester.cognito_user_id
        )

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        audit_event_log.target_user = user_service.get_user_by_domain_and_guid(
            application_admin_request.user_type_code,
            application_admin_request.user_guid,
        )
        if audit_event_log.target_user is None:
            audit_event_log.target_user = models.FamUser(
                user_type_code=application_admin_request.user_type_code,
                user_name=application_admin_request.user_name,
                user_guid="unknown",
                cognito_user_id="unknown",
            )

        audit_event_log.log_event()


@router.delete(
    "/{application_admin_id}",
    response_class=Response,
    dependencies=[
        Depends(authorize_by_fam_admin),
        Depends(enforce_self_grant_guard),
        Depends(validate_param_application_admin_id),
    ],
)
def delete_application_admin(
    application_admin_id: int,
    request: Request,
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
):
    LOGGER.debug(
        f"Executing 'delete_application_admin' with request: {application_admin_id}"
    )

    audit_event_log = AuditEventLog(
        request=request,
        event_type=AuditEventType.REMOVE_APPLICATION_ADMIN_ACCESS,
        event_outcome=AuditEventOutcome.SUCCESS,
    )

    try:
        application_admin_service = ApplicationAdminService(db)
        user_service = UserService(db)

        application_admin = application_admin_service.get_application_admin_by_id(
            application_admin_id
        )
        audit_event_log.requesting_user = user_service.get_user_by_cognito_user_id(
            requester.cognito_user_id
        )
        audit_event_log.application = application_admin.application
        audit_event_log.target_user = application_admin.user

        return application_admin_service.delete_application_admin(application_admin_id)

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        audit_event_log.log_event()
