import logging
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.orm import Session
from typing import List


from api.app.models import model as models
from api.app.routers.router_guards import (
    get_current_requester,
    authorize_by_fam_admin,
    enforce_self_grant_guard,
)
from api.app import database, jwt_validation, schemas
from api.app.schemas import Requester
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.user_service import UserService
from api.app.services.application_service import ApplicationService
from api.app.utils.audit_util import AuditEventLog, AuditEventOutcome, AuditEventType

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=schemas.FamAppAdminGet,
    dependencies=[Depends(authorize_by_fam_admin), Depends(enforce_self_grant_guard)],
)
def create_application_admin(
    application_admin_request: schemas.FamAppAdminCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize),
    requester: Requester = Depends(get_current_requester),
):

    LOGGER.debug(
        f"Executing 'create_user_role_assignment' "
        f"with request: {application_admin_request}, requestor: {token_claims}"
    )

    audit_event_log = AuditEventLog(
        request=request,
        event_type=AuditEventType.CREATE_APPLICATION_ADMIN_ACCESS,
        event_outcome=AuditEventOutcome.SUCCESS,
    )

    try:
        application_admin_service = ApplicationAdminService(db)
        application_service = ApplicationService(db)
        user_service = UserService(db)

        audit_event_log.requesting_user: models.FamUser = (
            user_service.get_user_by_cognito_user_id(requester.cognito_user_id)
        )
        audit_event_log.application: models.FamApplication = (
            application_service.get_application(
                application_admin_request.application_id
            )
        )
        audit_event_log.target_user: models.FamUser = (
            user_service.get_user_by_domain_and_name(
                application_admin_request.user_type_code,
                application_admin_request.user_name,
            )
        )

        return application_admin_service.create_application_admin(
            application_admin_request, requester.cognito_user_id
        )

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
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
    dependencies=[Depends(authorize_by_fam_admin), Depends(enforce_self_grant_guard)],
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
        if application_admin:
            audit_event_log.requesting_user: models.FamUser = (
                user_service.get_user_by_cognito_user_id(requester.cognito_user_id)
            )
            audit_event_log.application: models.FamApplication = (
                application_admin.application
            )
            audit_event_log.target_user: models.FamUser = application_admin.user

            return application_admin_service.delete_application_admin(
                application_admin_id
            )
        else:
            audit_event_log.event_outcome = AuditEventOutcome.FAIL
            audit_event_log.exception = HTTPException(
                status_code=404, detail="Application Admin id not exists"
            )

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        audit_event_log.log_event()


@router.get(
    "/{application_id}/admins",
    response_model=List[schemas.FamAppAdminGet],
    status_code=200,
    dependencies=[Depends(authorize_by_fam_admin)],
)
def get_application_admin_by_applicationid(
    application_id: int,
    db: Session = Depends(database.get_db),
):
    LOGGER.debug(
        f"Loading application admin access for application_id: {application_id}"
    )
    application_admin_service = ApplicationAdminService(db)
    application_admin_access = (
        application_admin_service.get_application_admin_by_applicationid(application_id)
    )
    LOGGER.debug(
        f"Finished loading application admin access for application - # of results = {len(application_admin_access)}"
    )

    return application_admin_access
