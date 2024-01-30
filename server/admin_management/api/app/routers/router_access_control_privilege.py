import logging
from typing import List

from api.app import jwt_validation, schemas
from api.app.models import model as models
from api.app.routers.router_guards import (
    authorize_by_application_role,
    authorize_by_app_id,
    enforce_self_grant_guard,
    get_current_requester,
)
from api.app.routers.router_utils import (
    access_control_privilege_service_instance,
    role_service_instance,
    user_service_instance,
)
from api.app.schemas import Requester
from api.app.services.access_control_privilege_service import (
    AccessControlPrivilegeService,
)
from api.app.services.role_service import RoleService
from api.app.services.user_service import UserService
from api.app.utils.audit_util import AuditEventLog, AuditEventOutcome, AuditEventType
from fastapi import APIRouter, Depends, Request


LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=List[schemas.FamAccessControlPrivilegeCreateResponse],
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
        forest_client_number=access_control_privilege_request.forest_client_numbers,
        event_outcome=AuditEventOutcome.SUCCESS,
    )

    try:
        audit_event_log.requesting_user = user_service.get_user_by_cognito_user_id(
            requester.cognito_user_id
        )
        audit_event_log.role = role_service.get_role_by_id(
            access_control_privilege_request.role_id
        )
        audit_event_log.application = audit_event_log.role.application
        audit_event_log.target_user = user_service.get_user_by_domain_and_name(
            access_control_privilege_request.user_type_code,
            access_control_privilege_request.user_name,
        )

        return access_control_privilege_service.create_access_control_privilege_many(
            access_control_privilege_request, requester.cognito_user_id
        )

    except Exception as e:
        audit_event_log.event_outcome = AuditEventOutcome.FAIL
        audit_event_log.exception = e
        raise e

    finally:
        if audit_event_log.target_user is None:
            audit_event_log.target_user = models.FamUser(
                user_type_code=access_control_privilege_request.user_type_code,
                user_name=access_control_privilege_request.user_name,
                user_guid="unknown",
                cognito_user_id="unknown",
            )

        audit_event_log.log_event()


@router.get(
    "/{application_id}/access_control_privileges",
    response_model=List[schemas.FamAccessControlPrivilegeDto],
    dependencies=[Depends(authorize_by_app_id)],  # only app admin can do this
    description="Get Delegated Admin Privileges For an Application",
)
def get_access_control_privileges_by_application_id(
    application_id: int,
    token_claims: dict = Depends(jwt_validation.authorize),
    access_control_privilege_service: AccessControlPrivilegeService = Depends(
        access_control_privilege_service_instance
    ),
):
    LOGGER.debug(
        f"Get access control privileges for application: {application_id}, requestor: {token_claims}"
    )

    return access_control_privilege_service.get_acp_by_application_id(application_id)
