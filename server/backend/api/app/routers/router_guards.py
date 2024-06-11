import logging
from http import HTTPStatus
from typing import List

from api.app import database
from api.app.constants import (
    ERROR_CODE_INVALID_REQUEST_PARAMETER,
    ERROR_CODE_SELF_GRANT_PROHIBITED,
    ERROR_CODE_INVALID_ROLE_ID,
    ERROR_CODE_REQUESTER_NOT_EXISTS,
    ERROR_CODE_EXTERNAL_USER_ACTION_PROHIBITED,
    ERROR_CODE_ACTION_NOT_NEEDED,
    ERROR_CODE_DIFFERENT_ORG_GRANT_PROHIBITED,
    ERROR_CODE_MISSING_KEY_ATTRIBUTE,
    UserType,
    RoleType,
)
from api.app.crud import (
    crud_role,
    crud_user,
    crud_user_role,
    crud_access_control_privilege,
    crud_utils,
)
from api.app.crud.validator.user_validator import UserValidator
from api.app.jwt_validation import (
    ERROR_PERMISSION_REQUIRED,
    ERROR_GROUPS_REQUIRED,
    JWT_GROUPS_KEY,
    get_access_roles,
    get_request_cognito_user_id,
    validate_token,
)
from api.app.models.model import FamRole, FamUser
from api.app.schemas import Requester, TargetUser
from api.app.utils import utils
from fastapi import Depends, Request
from sqlalchemy.orm import Session

"""
This file is intended to host functions only to guard the endpoints at framework's
router level BEFORE reaching withint the router logic (They should not be used
at crud(service) layer).
"""

LOGGER = logging.getLogger(__name__)


async def get_current_requester(
    request_cognito_user_id: str = Depends(get_request_cognito_user_id),
    access_roles: List[str] = Depends(get_access_roles),
    db: Session = Depends(database.get_db),
):
    LOGGER.debug(
        f"Debug router_guard get_current_requester, current request_cognito_user_id: {request_cognito_user_id}"
    )
    LOGGER.debug(
        f"Debug router_guard get_current_requester, current db connection: {db}"
    )
    fam_user: FamUser = crud_user.get_user_by_cognito_user_id(
        db, request_cognito_user_id
    )
    LOGGER.debug(
        f"Debug router_guard get_current_requester, current fam_user: {fam_user}"
    )
    if fam_user is None:
        utils.raise_http_exception(
            error_msg="Requester does not exist, action is not allowed.",
            error_code=ERROR_CODE_REQUESTER_NOT_EXISTS,
            status_code=HTTPStatus.FORBIDDEN,
        )

    requester = Requester.model_validate(fam_user)
    LOGGER.debug(
        f"Debug router_guard get_current_requester, current requester: {requester}"
    )
    requester.access_roles = access_roles
    LOGGER.debug(f"Current request user (requester): {requester}")
    return requester


def authorize(
    claims: dict = Depends(validate_token),
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
):
    """
    This authorize method is used by Forest Client API and IDIM Proxy API integration for a general authorization check,
    we require user to be the app admin or delegated admin of at least one application
    """
    if JWT_GROUPS_KEY not in claims or len(claims[JWT_GROUPS_KEY]) == 0:
        # if user has no application admin access
        # check if user has any delegated admin access
        requester_is_delegated_admin = crud_access_control_privilege.is_delegated_admin(
            db, requester.user_id
        )

        # if user is not app admin and not delegated admin of any application, throw miss access group error
        if not requester_is_delegated_admin:
            utils.raise_http_exception(
                status_code=HTTPStatus.FORBIDDEN,
                error_code=ERROR_GROUPS_REQUIRED,
                error_msg="At least one access group is required.",
            )


def authorize_by_app_id(
    application_id: int,
    db: Session = Depends(database.get_db),
    access_roles=Depends(get_access_roles),
    requester: Requester = Depends(get_current_requester),
):
    """
    This authorize_by_app_id method is used for the authorization check of a specific application,
    we require user to be the app admin or delegated admin of the application
    """
    requester_is_app_admin = crud_utils.is_app_admin(
        db=db, application_id=application_id, access_roles=access_roles
    )

    # if user is not application admin
    if not requester_is_app_admin:
        # check if user is application delegated admin
        requester_is_app_delegated_admin = (
            crud_access_control_privilege.is_delegated_admin_by_app_id(
                db, requester.user_id, application_id
            )
        )
        # if user is not app admin and not delegated admin of the application, throw permission error
        if not requester_is_app_delegated_admin:
            utils.raise_http_exception(
                status_code=HTTPStatus.FORBIDDEN,
                error_code=ERROR_PERMISSION_REQUIRED,
                error_msg="Requester has no admin or delegated admin access to the application.",
            )


async def get_request_role_from_id(
    request: Request, db: Session = Depends(database.get_db)
) -> FamRole:
    """
    (this is a sub-dependency as convenient function)
    To get role id from request...
    Some endpoints has path_params with "user_role_xref_id".
    Some endpoints has role_id in request body.
    """
    role = None

    if "user_role_xref_id" in request.path_params:
        user_role_xref_id = request.path_params["user_role_xref_id"]
        LOGGER.debug(f"Retrieving role by user_role_xref_id: " f"{user_role_xref_id}")
        user_role = crud_user_role.find_by_id(db, user_role_xref_id)
        role = user_role.role
    else:
        rbody = await request.json()
        role_id = rbody["role_id"]
        LOGGER.debug(f"Retrieving role by Request's role_id: {role_id}")
        role = crud_role.get_role(db, role_id)  # role could be None.

    if not role:
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_CODE_INVALID_ROLE_ID,
            error_msg="Role does not exist or failed to get the role_id from request.",
        )
    return role


def authorize_by_application_role(
    # Depends on "get_request_role_from_id()" to figure out
    # what id to use to get role from endpoint.
    role: FamRole = Depends(get_request_role_from_id),
    db: Session = Depends(database.get_db),
    access_roles=Depends(get_access_roles),
    requester: Requester = Depends(get_current_requester),
):
    """
    This authorize_by_application_role method is used for the authorization check of a specific application,
    it is the same and depends on the method authorize_by_app_id() but for
    the need that some routers contains target role_id in the request (instead of application_id)
    we need to get application_id from role and check if role exists first, and then call authorize_by_app_id()
    """
    # Delegate to this for main check.
    authorize_by_app_id(
        application_id=role.application_id,
        db=db,
        access_roles=access_roles,
        requester=requester,
    )
    return role


async def authorize_by_privilege(
    request: Request,
    role: FamRole = Depends(get_request_role_from_id),
    db: Session = Depends(database.get_db),
    access_roles=Depends(get_access_roles),
    requester: Requester = Depends(get_current_requester),
):
    """
    This authorize_by_privilege method is used for checking if the requester has the privilege to grant/remove access of the role.
    :param role: for remove access, it is the concrete role get by user_role_xref_id in the request params;
                 for grant access, it is the concrete role, or the parent role of an abstract role get by role_id in the request params
    """
    requester_is_app_admin = crud_utils.is_app_admin(
        role.application_id, db, access_roles
    )

    # if requester is not application admin, check if has the privilege to grant/remove access of the role
    if not requester_is_app_admin:
        # for remove access, role is what we get above from Depends(get_request_role_from_id)
        # for grant access, if the request params has forest_client_number, need to get the child role
        # the child role should already exist when the delegated admin has been created
        if "user_role_xref_id" not in request.path_params:
            rbody = await request.json()
            forest_client_number = rbody.get("forest_client_number")
            if (
                forest_client_number
                and role.role_type_code == RoleType.ROLE_TYPE_ABSTRACT
            ):
                parent_role = role
                forest_client_role_name = (
                    crud_user_role.construct_forest_client_role_name(
                        parent_role.role_name, forest_client_number
                    )
                )
                role = crud_role.get_role_by_role_name_and_app_id(
                    db, forest_client_role_name, parent_role.application_id
                )  # when role is None, means the role is not created for this delegated admin

        requester_has_privilege = False
        if role:
            requester_has_privilege = (
                crud_access_control_privilege.has_privilege_by_role_id(
                    db, requester.user_id, role.role_id
                )
            )
        # if user has no privilege of the role, throw permission error
        if not requester_has_privilege:
            utils.raise_http_exception(
                status_code=HTTPStatus.FORBIDDEN,
                error_code=ERROR_PERMISSION_REQUIRED,
                error_msg="Requester has no privilege to grant this access.",
            )


# Note!!
# currently to take care of different scenarios (id or fields needed in
# path/param/body) to find target user, will only consider request
# "path_params" and for "body"(json) for PUT/POST/DELETE.
# For now, only consider known cases ("router_user_role_assigment.py" endpoints
# that need this). Specifically: "user_role_xref_id" and
# "user_name/user_type_code".
# Very likely in future might have "cognito_user_id" case.
async def get_target_user_from_id(
    request: Request, db: Session = Depends(database.get_db)
) -> TargetUser:
    """
    This is used as FastAPI sub-dependency to find target_user for guard purpose.
    Please note that the TargetUser inputs hasn't been validated yet. Need to call get_verified_target_user to validate the TargetUser.
    For requester, use "get_current_requester()" above.
    """
    # from path_param - "user_role_xref_id"; should exists already in db.
    if "user_role_xref_id" in request.path_params:
        urxid = request.path_params["user_role_xref_id"]
        LOGGER.debug(
            "Dependency 'get_target_user_from_id' called with "
            + f"request containing user_role_xref_id path param {urxid}."
        )
        user_role = crud_user_role.find_by_id(db, urxid)
        if user_role is not None:
            found_target_user = TargetUser.model_validate(user_role.user)
            return found_target_user
        else:
            error_msg = "Parameter 'user_role_xref_id' is missing or invalid."
            utils.raise_http_exception(
                error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER, error_msg=error_msg
            )

    else:
        # from request body - {user_name/user_type_code}
        rbody = await request.json()
        LOGGER.debug(
            "Dependency 'get_target_user_from_id' called with "
            + f"request body {rbody}."
        )
        target_new_user = TargetUser.model_validate(
            {
                "user_name": rbody["user_name"],
                "user_type_code": rbody["user_type_code"],
                "user_guid": rbody["user_guid"],
            }
        )
        return target_new_user


async def authorize_by_user_type(
    requester: Requester = Depends(get_current_requester),
    target_user: TargetUser = Depends(get_target_user_from_id),
):
    """
    This authorize_by_user_type method is used to forbidden business bceid user manage idir user's access
    """
    if requester.user_type_code == UserType.BCEID:
        target_user_type_code = target_user.user_type_code

        if not target_user_type_code:
            error_msg = "Operation encountered unexpected error. Target user user_type code is missing."
            utils.raise_http_exception(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                error_code=ERROR_CODE_MISSING_KEY_ATTRIBUTE,
                error_msg=error_msg,
            )

        if target_user_type_code == UserType.IDIR:
            utils.raise_http_exception(
                status_code=HTTPStatus.FORBIDDEN,
                error_code=ERROR_PERMISSION_REQUIRED,
                error_msg="Business BCEID requester has no privilege to grant this access to IDIR user.",
            )


async def internal_only_action(requester: Requester = Depends(get_current_requester)):
    if requester.user_type_code is not UserType.IDIR:
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_CODE_EXTERNAL_USER_ACTION_PROHIBITED,
            error_msg="Action is not allowed for external user.",
        )


async def requester_is_external_delegated_admin(
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
):
    if (
        requester.user_type_code is UserType.BCEID
        and crud_access_control_privilege.is_delegated_admin(db, requester.user_id)
    ):
        return True
    return False


async def external_delegated_admin_only_action(
    is_external_delegated_admin: bool = Depends(requester_is_external_delegated_admin),
):
    if not is_external_delegated_admin:
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_CODE_ACTION_NOT_NEEDED,
            error_msg="Action is not needed",
        )


async def enforce_self_grant_guard(
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
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_CODE_SELF_GRANT_PROHIBITED,
            error_msg="Altering permission privilege to self is not allowed.",
        )


async def get_verified_target_user(
    requester: Requester = Depends(get_current_requester),
    target_user: TargetUser = Depends(get_target_user_from_id),
) -> TargetUser:
    """
    Validate the target user by calling IDIM web service, and update business Guid for the found BCeID user
    """
    user_validator = UserValidator(requester, target_user)
    return user_validator.verify_user_exist()


async def enforce_bceid_by_same_org_guard(
    # forbid business bceid user (requester) manage idir user's access
    _enforce_user_type_auth: None = Depends(authorize_by_user_type),
    requester: Requester = Depends(get_current_requester),
    target_user: TargetUser = Depends(get_verified_target_user),
):
    """
    When requester is a BCeID user, enforce requester can only manage target
    user from the same organization.
    :param _enforce_user_type_auth: call the authorize_by_user_type method
            to ensure that this enforce_bceid_by_same_org_guard method only
            checks when business bceid user grants access to another business
            bceid user
    """
    LOGGER.debug(
        f"Verifying requester {requester.user_name} (type {requester.user_type_code}) "
        "is allowed to manage BCeID target user for the same organization."
    )
    if requester.user_type_code == UserType.BCEID:
        requester_business_guid = requester.business_guid
        target_user_business_guid = target_user.business_guid

        if requester_business_guid is None or target_user_business_guid is None:
            error_msg = "Operation encountered unexpected error. Requester or target user business GUID is missing."
            utils.raise_http_exception(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                error_code=ERROR_CODE_MISSING_KEY_ATTRIBUTE,
                error_msg=error_msg,
            )

        elif requester_business_guid.upper() != target_user_business_guid.upper():
            utils.raise_http_exception(
                status_code=HTTPStatus.FORBIDDEN,
                error_code=ERROR_CODE_DIFFERENT_ORG_GRANT_PROHIBITED,
                error_msg="Managing for different organization is not allowed.",
            )
