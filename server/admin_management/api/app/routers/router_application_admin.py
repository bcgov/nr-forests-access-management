import logging
from datetime import datetime
from typing import List

from api.app import database, jwt_validation
from api.app.models.model import FamUser
from api.app.routers.router_guards import (authorize_by_fam_admin,
                                           enforce_self_grant_guard,
                                           get_current_requester,
                                           get_verified_target_user,
                                           validate_param_application_admin_id,
                                           validate_param_application_id,
                                           validate_param_user_type)
from api.app.routers.router_utils import (application_admin_service_instance,
                                          application_service_instance,
                                          csv_file_data_streamer,
                                          user_service_instance)
from api.app.schemas import schemas
from api.app.schemas.schemas import Requester, TargetUser
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.application_service import ApplicationService
from api.app.services.user_service import UserService
from api.app.utils.audit_util import (AuditEventLog, AuditEventOutcome,
                                      AuditEventType)
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import StreamingResponse
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


@router.get(
    "/export",
    dependencies=[Depends(authorize_by_fam_admin)],
    summary="Export application admins information",
)
async def export_application_admins(
    application_admin_service: ApplicationAdminService = Depends(
        application_admin_service_instance
    ),
):
    results: List[schemas.FamAppAdminGetResponse] = application_admin_service.get_application_admins()
    filename = f"FAM_app_admins-{datetime.now().strftime('%Y-%m-%d')}.csv"
    return StreamingResponse(__export_appplication_admin_csv_file(results), media_type="text/csv", headers={
        "Access-Control-Expose-Headers":"Content-Disposition",
        "Content-Disposition": f"attachment; filename={filename}"
    })


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
        audit_event_log.requesting_user = requester
        audit_event_log.application = application_service.get_application(
            application_admin_request.application_id
        )

        response = application_admin_service.create_application_admin(
            application_admin_request, target_user, requester
        )

        # get target user from database, so for existing user, we can get the cognito user id
        audit_event_log.target_user = user_service.get_user_by_domain_and_guid(
            application_admin_request.user_type_code,
            application_admin_request.user_guid,
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
        application_admin = application_admin_service.get_application_admin_by_id(
            application_admin_id
        )
        audit_event_log.requesting_user = requester
        audit_event_log.application = application_admin.application
        audit_event_log.target_user = application_admin.user

        return application_admin_service.delete_application_admin(requester, application_admin_id)

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        audit_event_log.log_event()


def __export_appplication_admin_csv_file(data: List[schemas.FamAppAdminGetResponse]):
    """
    This is a private helper function to export the application admin assignments data to a CSV file.
    """
    ini_title_line = "FAM Application Admin"
    csv_rows = [
        {
            "User Name": item.user.user_name,
            "Domain": item.user.user_type_relation.description,
            "First Name": item.user.first_name,
            "Last Name": item.user.last_name,
            "Email": item.user.email,
            "Application": f"'{item.application.application_description}'",
            "Environment": item.application.app_environment,
            "Role Enable To Assign": "Admin"
        } for item in data]
    return csv_file_data_streamer(ini_title_line=ini_title_line, data=csv_rows)