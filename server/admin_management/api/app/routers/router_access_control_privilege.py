import logging
from typing import List

from api.app import jwt_validation, schemas
from api.app.models.model import FamUser
from api.app.routers.router_guards import (
    authorize_by_app_id, authorize_by_application_role,
    enforce_self_grant_guard, get_current_requester, get_verified_target_user,
    validate_param_access_control_privilege_id)
from api.app.routers.router_utils import (
    access_control_privilege_service_instance, role_service_instance,
    user_service_instance)
from api.app.schemas import (FamAccessControlPrivilegeResponse, Requester,
                             TargetUser)
from api.app.services.access_control_privilege_service import \
    AccessControlPrivilegeService
from api.app.services.role_service import RoleService
from api.app.services.user_service import UserService
from api.app.utils.audit_util import (AuditEventLog, AuditEventOutcome,
                                      AuditEventType)
from fastapi import APIRouter, Depends, Request, Response

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=schemas.FamAccessControlPrivilegeResponse,
    dependencies=[
        Depends(
            authorize_by_application_role
        ),  # only app admin can do this, get application by role
        Depends(enforce_self_grant_guard),
    ],
    description="Grant Delegated Admin Privileges",
)
def create_access_control_privilege_many(
    access_control_privilege_request: schemas.FamAccessControlPrivilegeCreateRequest,
    request: Request,
    token_claims: dict = Depends(jwt_validation.authorize),
    requester: Requester = Depends(get_current_requester),
    target_user: TargetUser = Depends(get_verified_target_user),
    user_service: UserService = Depends(user_service_instance),
    role_service: RoleService = Depends(role_service_instance),
    access_control_privilege_service: AccessControlPrivilegeService = Depends(
        access_control_privilege_service_instance
    ),
):
    """
    If grant delegated admin access privilege to a concrete role, no need to provide the forest client number.
    If grant delegated admin access privilege to an abstract role, need to provide a list of forest client numbers,
    and this post method will create the access control privileges for each of them.

    param: the request parameter includes user name, user type code, role id and a list of ofrest client numbers

    return: a list of creation results for each forest client number
    """

    LOGGER.debug(
        f"Executing 'create_access_control_privilege_many' "
        f"with request: {access_control_privilege_request}, requestor: {token_claims}"
    )

    audit_event_log = AuditEventLog(
        request=request,
        event_type=AuditEventType.CREATE_ACCESS_CONTROL_PRIVILIEGE,
        forest_client_numbers=access_control_privilege_request.forest_client_numbers,
        event_outcome=AuditEventOutcome.SUCCESS,
    )

    try:
        audit_event_log.requesting_user = requester
        audit_event_log.role = role_service.get_role_by_id(
            access_control_privilege_request.role_id
        )
        audit_event_log.application = audit_event_log.role.application

        response = FamAccessControlPrivilegeResponse(
            assignments_detail=access_control_privilege_service.create_access_control_privilege_many(
                access_control_privilege_request, requester.cognito_user_id, target_user
            )
        )

        # get target user from database, so for existing user, we can get the cognito user id
        audit_event_log.target_user = user_service.get_user_by_domain_and_guid(
            access_control_privilege_request.user_type_code,
            access_control_privilege_request.user_guid,
        )

        # Send email notification if required
        if access_control_privilege_request.requires_send_user_email:
            response.email_sending_status = access_control_privilege_service.send_email_notification(
                target_user, response.assignments_detail
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


@router.get(
    "",
    response_model=List[schemas.FamAccessControlPrivilegeGetResponse],
    status_code=200,
    dependencies=[Depends(authorize_by_app_id)],  # only app admin can do this
    description="Get Delegated Admin Privileges For an Application",
)
def get_access_control_privileges_by_application_id(
    application_id: int,
    access_control_privilege_service: AccessControlPrivilegeService = Depends(
        access_control_privilege_service_instance
    ),
):
    return access_control_privilege_service.get_acp_by_application_id(application_id)


@router.delete(
    "/{access_control_privilege_id}",
    response_class=Response,
    dependencies=[
        Depends(
            validate_param_access_control_privilege_id
        ),  # validate id first, otherwise authorize_by_application_role cannot find application by role
        Depends(
            authorize_by_application_role
        ),  # only app admin can do this, get application by role
        Depends(enforce_self_grant_guard),
    ],
)
def delete_access_control_privilege(
    access_control_privilege_id: int,
    request: Request,
    access_control_privilege_service: AccessControlPrivilegeService = Depends(
        access_control_privilege_service_instance
    ),
    requester: Requester = Depends(get_current_requester),
):
    LOGGER.debug(
        f"Executing 'delete_access_control_privilege' with request: {access_control_privilege_id}"
    )

    audit_event_log = AuditEventLog(
        request=request,
        event_type=AuditEventType.REMOVE_ACCESS_CONTROL_PRIVILIEGE,
        event_outcome=AuditEventOutcome.SUCCESS,
    )

    try:
        audit_event_log.requesting_user = requester
        access_control_privilege = access_control_privilege_service.get_acp_by_id(
            access_control_privilege_id
        )
        audit_event_log.role = access_control_privilege.role
        audit_event_log.application = access_control_privilege.role.application
        audit_event_log.target_user = access_control_privilege.user

        return access_control_privilege_service.delete_access_control_privilege(
            access_control_privilege_id
        )

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        audit_event_log.log_event()
