import json
import logging
from http import HTTPStatus
from typing import Union

from api.app.constants import (ERROR_CODE_INVALID_REQUEST_PARAMETER,
                               AdminRoleAuthGroup, UserType)
from api.app.jwt_validation import (
    ERROR_PERMISSION_REQUIRED, get_access_roles, get_request_cognito_user_id,
    get_request_cognito_user_id_without_access_check, validate_token)
from api.app.models.model import FamRole, FamUser
from api.app.routers.router_utils import (
    access_control_privilege_service_instance,
    application_admin_service_instance, application_service_instance,
    role_service_instance, user_service_instance)
from api.app.schemas.schemas import (FamAppAdminCreateRequest, Requester,
                                     TargetUser)
from api.app.services import utils_service
from api.app.services.access_control_privilege_service import \
    AccessControlPrivilegeService
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.application_service import ApplicationService
from api.app.services.role_service import RoleService
from api.app.services.user_service import UserService
from api.app.services.validator.target_user_validator import \
    TargetUserValidator
from api.app.utils import utils
from fastapi import Depends, HTTPException, Request

LOGGER = logging.getLogger(__name__)


ERROR_SELF_GRANT_PROHIBITED = "self_grant_prohibited"
ERROR_INVALID_APPLICATION_ID = "invalid_application_id"
ERROR_INVALID_ROLE_ID = "invalid_role_id"
ERROR_REQUESTER_NOT_EXISTS = "requester_not_exists"
ERROR_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"
ERROR_INVALID_APPLICATION_ADMIN_ID = "invalid_application_admin_id"
ERROR_INVALID_ACCESS_CONTROL_PRIVILEGE_ID = "invalid_access_control_privilege_id"
ERROR_NOT_ALLOWED_USER_TYPE = "user_type_not_allowed"

no_requester_exception = HTTPException(
    status_code=HTTPStatus.FORBIDDEN,  # 403
    detail={
        "code": ERROR_REQUESTER_NOT_EXISTS,
        "description": "Requester does not exist, action is not allowed",
    },
)


def authorize_by_fam_admin(claims: dict = Depends(validate_token)):
    required_role = AdminRoleAuthGroup.FAM_ADMIN
    access_roles = get_access_roles(claims)

    if required_role not in access_roles:
        error_msg = f"Operation requires role {required_role}."
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_PERMISSION_REQUIRED,
            error_msg=error_msg,
        )


# for app admin and FAM admin, we require the access group in the token
# the get_request_cognito_user_id will check the access in the token
def get_current_requester(
    request_cognito_user_id: str = Depends(get_request_cognito_user_id),
    access_roles=Depends(get_access_roles),
    user_service: UserService = Depends(user_service_instance),
):
    fam_user: FamUser = user_service.get_user_by_cognito_user_id(
        request_cognito_user_id
    )
    if fam_user is None:
        raise no_requester_exception

    requester = Requester.model_validate(fam_user)
    requester.access_roles = access_roles
    LOGGER.debug(f"Current request user (requester): {requester}")
    return requester


# for delegated admin, there is no access group in the token, our auth lambda function only add app admin to the token
# get_request_cognito_user_id_without_access_check will return the requester without checking the access group in the token
# this should only used by the get_admin_user_access API, all other APIs require admin access in the token
def get_current_requester_without_access_check(
    request_cognito_user_id: str = Depends(
        get_request_cognito_user_id_without_access_check
    ),
    user_service: UserService = Depends(user_service_instance),
):
    fam_user: FamUser = user_service.get_user_by_cognito_user_id(
        request_cognito_user_id
    )
    if fam_user is None:
        raise no_requester_exception

    requester = Requester.model_validate(fam_user)
    LOGGER.debug(f"Current request user (requester): {requester}")
    return requester


# Note!!
# currently to take care of different scenarios (id or fields needed in path/param/body)
# to find target user, will only consider request "path_params" and "body"(json) for PUT/POST.
# For now, only consider known cases.
# Specifically: "application_admin_id", "access_control_privilege_id" and
# "user_name/user_type_code" in request body.
# Very likely in future might have "cognito_user_id" case.
async def get_target_user_from_id(
    request: Request,
    application_admin_service: ApplicationAdminService = Depends(
        application_admin_service_instance
    ),
    access_control_privilege_service: AccessControlPrivilegeService = Depends(
        access_control_privilege_service_instance
    ),
) -> TargetUser:
    """
    This is used as FastAPI sub-dependency to find target_user for guard purpose.
    Please note that the TargetUser inputs hasn't been validated yet. Need to call get_verified_target_user to validate the TargetUser.
    For requester, use "get_current_requester()".
    """
    # from path_param - application_admin_id, when remove admin access for a user
    if "application_admin_id" in request.path_params:
        raaid = request.path_params["application_admin_id"]
        LOGGER.debug(
            "Dependency 'get_target_user_from_id': 'application_admin_id' "
            + f"path param found: {raaid}."
        )
        application_admin = application_admin_service.get_application_admin_by_id(raaid)
        if application_admin is not None:
            return TargetUser.model_validate(application_admin.user)
        else:
            error_msg = (
                "Parameter 'application_admin_id' {raaid} is missing or invalid."
            )
            utils.raise_http_exception(
                error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER, error_msg=error_msg
            )

    elif "access_control_privilege_id" in request.path_params:
        acpid = request.path_params["access_control_privilege_id"]
        LOGGER.debug(
            "Dependency 'get_target_user_from_id': 'access_control_privilege_id' "
            + f"path param found: {acpid}."
        )
        access_control_privilege = access_control_privilege_service.get_acp_by_id(acpid)
        if access_control_privilege is not None:
            return TargetUser.model_validate(access_control_privilege.user)
        else:
            error_msg = (
                "Parameter 'access_control_privilege_id' {acpid} is missing or invalid."
            )
            utils.raise_http_exception(
                error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER, error_msg=error_msg
            )
    else:
        # from body - {user_name/user_type_code/user_guid}, when grant admin access
        rbody = await request.json()
        LOGGER.debug(f"Dependency 'get_target_user_from_id' request body {rbody}.")

        target_new_user = TargetUser.model_validate(
            {
                "user_name": rbody["user_name"],
                "user_type_code": rbody["user_type_code"],
                "user_guid": rbody["user_guid"],
            }
        )
        return target_new_user


async def get_request_role_from_id(
    request: Request,
    access_control_privilege_service: AccessControlPrivilegeService = Depends(
        access_control_privilege_service_instance
    ),
    role_service: RoleService = Depends(role_service_instance),
) -> Union[FamRole, None]:
    """
    To get role from request
    For deleting access control privilege method, get the role by access_control_privilege_id
    For adding access control privilege method, get role through request data
    """
    access_control_privilege_id = None
    if "access_control_privilege_id" in request.path_params:
        access_control_privilege_id = request.path_params["access_control_privilege_id"]

    if access_control_privilege_id:
        access_control_privilege = access_control_privilege_service.get_acp_by_id(
            access_control_privilege_id
        )
        return access_control_privilege.role
    else:
        try:
            rbody = await request.json()
            role_id = rbody.get("role_id")
            role = role_service.get_role_by_id(role_id)
            return role  # role could be None.

        # When request does not contains body part.
        except json.JSONDecodeError:
            return None


def get_verified_target_user(
    requester: Requester = Depends(get_current_requester),
    target_user: TargetUser = Depends(get_target_user_from_id),
    role: FamRole = Depends(get_request_role_from_id),
) -> TargetUser:
    """
    Validate the target user by calling IDIM web service, and update business Guid for the found BCeID user
    """
    # ignore the role validation here, cause we have other router guards to do that when grant/delete delegated admin
    # in the case that role is none, that's for granting/deleting application admin with FAM, which has no app_env
    app_env = role.application.app_environment if role and role.application else None
    api_instance_env = utils_service.use_api_instance_by_app_env(app_env)
    LOGGER.debug(f"For application operation on: {api_instance_env}")
    target_user_validator = TargetUserValidator(
        requester, target_user, api_instance_env
    )
    return target_user_validator.verify_user_exist()


def enforce_self_grant_guard(
    requester: Requester = Depends(get_current_requester),
    target_user: TargetUser = Depends(get_target_user_from_id),
):
    """
    Verify logged on admin (requester):
        Self granting/removing privilege currently isn't allowed.
    """
    LOGGER.debug(f"enforce_self_grant_guard: requester - {requester}")
    LOGGER.debug(f"enforce_self_grant_guard: target_user - {target_user}")

    if (
        requester.user_type_code == target_user.user_type_code
        and requester.user_guid == target_user.user_guid
    ):
        LOGGER.debug(
            f"User '{requester.user_name}' should not "
            f"grant/remove permission privilege to self."
        )
        error_msg = "Altering permission privilege to self is not allowed."
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_SELF_GRANT_PROHIBITED,
            error_msg=error_msg,
        )


def authorize_by_application_role(
    # Depends on "get_request_role_from_id()" to figure out
    # what id to use to get role from endpoint.
    role: FamRole = Depends(get_request_role_from_id),
    claims: dict = Depends(validate_token),
    application_service: ApplicationService = Depends(application_service_instance),
):
    """
    This router validation is currently design to validate logged on "admin"
    has authority to perform actions for application with roles in [app]_ADMIN.
    This function basically is the same and depends on (authorize_by_app_id()) but for
    the need that some routers contains target role_id in the request (instead of application_id).
    Check if role exists or not
    """
    if not role:
        error_msg = "Requester has no appropriate role."
        utils.raise_http_exception(
            error_code=ERROR_INVALID_ROLE_ID, error_msg=error_msg
        )

    authorize_by_app_id(role.application_id, claims, application_service)
    return role


def authorize_by_app_id(
    application_id: int,
    claims: dict = Depends(validate_token),
    application_service: ApplicationService = Depends(application_service_instance),
):
    application = application_service.get_application(application_id)
    if not application:
        error_msg = f"Application ID {application_id} not found."
        utils.raise_http_exception(
            error_code=ERROR_INVALID_APPLICATION_ID, error_msg=error_msg
        )

    required_role = f"{application.application_name.upper()}_ADMIN"
    access_roles = get_access_roles(claims)

    if required_role not in access_roles:
        error_msg = f"Operation requires role {required_role}."
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_PERMISSION_REQUIRED,
            error_msg=error_msg,
        )


def validate_param_application_admin_id(
    application_admin_id: int,
    application_admin_service: ApplicationAdminService = Depends(
        application_admin_service_instance
    ),
):
    application_admin = application_admin_service.get_application_admin_by_id(
        application_admin_id
    )
    if not application_admin:
        error_msg = f"Application Admin ID {application_admin_id} not found."
        utils.raise_http_exception(
            error_code=ERROR_INVALID_APPLICATION_ADMIN_ID, error_msg=error_msg
        )


def validate_param_application_id(
    application_admin_request: FamAppAdminCreateRequest,
    application_service: ApplicationService = Depends(application_service_instance),
):
    application = application_service.get_application(
        application_admin_request.application_id
    )
    if not application:
        error_msg = (
            f"Application ID {application_admin_request.application_id} not found."
        )
        utils.raise_http_exception(
            error_code=ERROR_INVALID_APPLICATION_ID, error_msg=error_msg
        )


def validate_param_user_type(application_admin_request: FamAppAdminCreateRequest):
    if (
        not application_admin_request.user_type_code
        or application_admin_request.user_type_code != UserType.IDIR
    ):
        error_msg = (
            f"User type {application_admin_request.user_type_code} is not allowed."
        )
        utils.raise_http_exception(
            error_code=ERROR_NOT_ALLOWED_USER_TYPE, error_msg=error_msg
        )


def validate_param_access_control_privilege_id(
    access_control_privilege_id: int,
    access_control_privilege_service: AccessControlPrivilegeService = Depends(
        access_control_privilege_service_instance
    ),
):
    access_control_privilege = access_control_privilege_service.get_acp_by_id(
        access_control_privilege_id
    )
    if not access_control_privilege:
        error_msg = (
            f"Access control privilege ID {access_control_privilege_id} not found."
        )
        utils.raise_http_exception(
            error_code=ERROR_INVALID_ACCESS_CONTROL_PRIVILEGE_ID, error_msg=error_msg
        )