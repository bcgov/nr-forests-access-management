from api.app.crud.validator.target_user_validator import (validate_target_users,
                                                    validate_bceid_same_org)
import logging
from http import HTTPStatus
from typing import List

from api.app import database
from api.app.constants import (CURRENT_TERMS_AND_CONDITIONS_VERSION,
                               ERROR_CODE_DIFFERENT_ORG_GRANT_PROHIBITED,
                               ERROR_CODE_EXTERNAL_USER_ACTION_PROHIBITED,
                               ERROR_CODE_INVALID_OPERATION,
                               ERROR_CODE_INVALID_REQUEST_PARAMETER,
                               ERROR_CODE_INVALID_ROLE_ID,
                               ERROR_CODE_MISSING_KEY_ATTRIBUTE,
                               ERROR_CODE_REQUESTER_NOT_EXISTS,
                               ERROR_CODE_SELF_GRANT_PROHIBITED,
                               ERROR_CODE_TERMS_CONDITIONS_REQUIRED,
                               ERROR_CODE_UNKNOWN_STATE, RoleType, UserType)
from api.app.crud import (crud_access_control_privilege, crud_application,
                          crud_role, crud_user, crud_user_role, crud_utils)
from api.app.jwt_validation import (ERROR_GROUPS_REQUIRED,
                                    ERROR_PERMISSION_REQUIRED, JWT_GROUPS_KEY,
                                    enforce_fam_client_token, get_access_roles,
                                    get_request_app_client_id,
                                    get_request_cognito_user_id,
                                    validate_token)
from api.app.models.model import FamRole, FamUser
from api.app.schemas import RequesterSchema, TargetUserSchema
from api.app.schemas.fam_application import FamApplicationSchema
from api.app.utils import utils
from api.config import config
from fastapi import Depends, Request, Security
from fastapi.security import APIKeyHeader
from api.app.schemas.target_user_validation_result import TargetUserValidationResultSchema
from sqlalchemy.orm import Session

"""
This file is intended to host functions only to guard the endpoints at framework's
router level BEFORE reaching withint the router logic (They should not be used
at crud(service) layer).
"""

LOGGER = logging.getLogger(__name__)
x_api_key = APIKeyHeader(name="X-API-Key")


def get_current_requester(
    request_cognito_user_id: str = Depends(get_request_cognito_user_id),
    access_roles: List[str] = Depends(get_access_roles),
    db: Session = Depends(database.get_db),
) -> RequesterSchema:
    LOGGER.debug(
        f"Retrieving current Requester from: request_cognito_user_id: {request_cognito_user_id}"
    )
    fam_user: FamUser = crud_user.fetch_initial_requester_info(
        db, request_cognito_user_id
    )
    LOGGER.debug(f"Current retrieved fam_user: {fam_user}")

    if fam_user is None:
        utils.raise_http_exception(
            error_msg="Requester does not exist, action is not allowed.",
            error_code=ERROR_CODE_REQUESTER_NOT_EXISTS,
            status_code=HTTPStatus.FORBIDDEN,
        )

    else:
        custom_fields = _parse_custom_requester_fields(fam_user)
        requester = RequesterSchema.model_validate(
            {
                **fam_user.__dict__,  # base db 'user' info
                "access_roles": access_roles,  # role from JWT
                **custom_fields,  # build/convert to custom attributes
            }
        )
        LOGGER.debug(f"Current request user (Requester): {requester}")
        return requester


def _parse_custom_requester_fields(fam_user: FamUser):
    """
    Conversation helper function to parse information from FamUser for some
    custom attributes needed at Requester.
    :fam_user: fetched FamUser from db with joined table information.
    :return: dictionary contains custom attributes information for setting 'Requester'
    """
    user_type_code = fam_user.user_type_code
    is_delegated_admin = len(fam_user.fam_access_control_privileges) > 0
    has_current_terms_conditions_accepted = (
        fam_user.fam_user_terms_conditions
        and fam_user.fam_user_terms_conditions.version
        == CURRENT_TERMS_AND_CONDITIONS_VERSION
    )
    requires_accept_tc = (
        user_type_code == UserType.BCEID
        and is_delegated_admin
        and not has_current_terms_conditions_accepted
    )

    return {
        "is_delegated_admin": is_delegated_admin,
        "requires_accept_tc": requires_accept_tc,
    }


def authorize(
    claims: dict = Depends(enforce_fam_client_token),
    requester: RequesterSchema = Depends(get_current_requester),
):
    """
    This authorize method is used by Forest Client API and IDIM Proxy API integration for a general authorization check,
    we require user to be the app admin or delegated admin of at least one application
    """
    if JWT_GROUPS_KEY not in claims or len(claims[JWT_GROUPS_KEY]) == 0:
        # if user has no application admin access
        # check if user has any delegated admin access

        # if user is not app admin and not delegated admin of any application, throw miss access group error
        if not requester.is_delegated_admin:
            utils.raise_http_exception(
                status_code=HTTPStatus.FORBIDDEN,
                error_code=ERROR_GROUPS_REQUIRED,
                error_msg="At least one access group is required.",
            )


def authorize_by_app_id(
    application_id: int,
    _enforce_fam_access_validated = Depends(enforce_fam_client_token),
    db: Session = Depends(database.get_db),
    access_roles=Depends(get_access_roles),
    requester: RequesterSchema = Depends(get_current_requester),
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
    _enforce_fam_access_validated = Depends(enforce_fam_client_token),
    role: FamRole = Depends(get_request_role_from_id),
    db: Session = Depends(database.get_db),
    access_roles=Depends(get_access_roles),
    requester: RequesterSchema = Depends(get_current_requester),
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
    _enforce_fam_access_validated = Depends(enforce_fam_client_token),
    role: FamRole = Depends(get_request_role_from_id),
    db: Session = Depends(database.get_db),
    access_roles=Depends(get_access_roles),
    requester: RequesterSchema = Depends(get_current_requester),
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
        if "user_role_xref_id" not in request.path_params:
            # for grant access with abstract role, if the request params has forest_client_numbers, need to get the child role
            # the child role should already exist when the delegated admin has been created
            rbody = await request.json()
            forest_client_numbers = rbody.get("forest_client_numbers")
            if (
                forest_client_numbers
                and role.role_type_code == RoleType.ROLE_TYPE_ABSTRACT
            ):
                parent_role = role
                for forest_client_number in forest_client_numbers:
                    forest_client_role_name = (
                        crud_user_role.construct_forest_client_role_name(
                            parent_role.role_name, forest_client_number
                        )
                    )
                    role = crud_role.get_role_by_role_name_and_app_id(
                        db, forest_client_role_name, parent_role.application_id
                    )  # when role is None, means the role is not created for this delegated admin
                    if (
                        not role
                        or not crud_access_control_privilege.has_privilege_by_role_id(
                            db, requester.user_id, role.role_id
                        )
                    ):
                        # if user has no privilege of the role, throw permission error
                        utils.raise_http_exception(
                            status_code=HTTPStatus.FORBIDDEN,
                            error_code=ERROR_PERMISSION_REQUIRED,
                            error_msg="Requester has no privilege to grant this access.",
                        )

        # for remove access and grant access with concrete, role is what we get above from Depends(get_request_role_from_id)
        if not role or not crud_access_control_privilege.has_privilege_by_role_id(
            db, requester.user_id, role.role_id
        ):
            # if user has no privilege of the role, throw permission error
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
async def get_target_users_from_ids(
    request: Request, db: Session = Depends(database.get_db)
) -> list[TargetUserSchema]:
    """
    FastAPI dependency to extract target users for guard purposes.
    Note, it will call IDIM service to verify user existence for each target user.
    For Requesting user, use "get_current_requester" dependency.

    Request field convention:
    - For a single user: request body should be a dict with keys 'user_name', 'user_type_code', 'user_guid'.
    - For multiple users: request body should contain a 'target_users' key with a list of user dicts.
      Example:
          {
              "target_users": [
                  {"user_name": "jdoe", "user_type_code": "IDIR", "user_guid": "abc-123"},
                  {"user_name": "asmith", "user_type_code": "BCEID", "user_guid": "def-456"}
              ]
          }
    The method will always return a list of TargetUserSchema objects.
    """
    target_users = []
    # from path_param - "user_role_xref_id"; should exist already in db.
    if "user_role_xref_id" in request.path_params:
        urxid = request.path_params["user_role_xref_id"]
        LOGGER.debug(
            "Dependency 'get_target_users_from_ids' called with "
            + f"request containing user_role_xref_id path param {urxid}."
        )
        user_role = crud_user_role.find_by_id(db, urxid)
        if user_role is not None:
            found_target_user = TargetUserSchema.model_validate(user_role.user)
            target_users.append(found_target_user)
        else:
            error_msg = "Parameter 'user_role_xref_id' is missing or invalid."
            utils.raise_http_exception(
                error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER, error_msg=error_msg
            )
    else:
        # from request body - support single or multiple users
        rbody = await request.json()
        LOGGER.debug(
            "Dependency 'get_target_users_from_ids' called with "
            + f"request body {rbody}."
        )
        # Accept either a single user dict or a list of user dicts
        user_items = rbody.get("users") or [rbody]
        for user_item in user_items:
            target_user = TargetUserSchema.model_validate({
                "user_name": user_item["user_name"],
                "user_type_code": rbody["user_type_code"],
                "user_guid": user_item["user_guid"],
            })
            target_users.append(target_user)
    return target_users


def authorize_by_user_type(
    requester: RequesterSchema = Depends(get_current_requester),
    target_users: list[TargetUserSchema] = Depends(get_target_users_from_ids),
):
    """
    This authorize_by_user_type method is used to forbid business bceid user managing idir user's access.
    """
    if requester.user_type_code == UserType.BCEID:
        for target_user in target_users:
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


def internal_only_action(
    _enforce_fam_access_validated = Depends(enforce_fam_client_token),
    requester: RequesterSchema = Depends(get_current_requester),
):
    if requester.user_type_code is not UserType.IDIR:
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_CODE_EXTERNAL_USER_ACTION_PROHIBITED,
            error_msg="Action is not allowed for external user.",
        )


def external_delegated_admin_only_action(
    _enforce_fam_access_validated = Depends(enforce_fam_client_token),
    requester: RequesterSchema = Depends(get_current_requester),
):
    if not requester.is_external_delegated_admin():
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_CODE_INVALID_OPERATION,
            error_msg="Action is not needed",
        )


def enforce_self_grant_guard(
    _enforce_fam_access_validated = Depends(enforce_fam_client_token),
    requester: RequesterSchema = Depends(get_current_requester),
    target_users: list[TargetUserSchema] = Depends(get_target_users_from_ids),
):
    """
    Verify logged on admin (RequesterSchema):
        Self granting/removing privilege currently isn't allowed.
        Supports multi-user: checks all target users in the list.
    """
    LOGGER.debug(f"enforce_self_grant_guard: requester - {requester}")
    LOGGER.debug(f"enforce_self_grant_guard: target_users - {target_users}")

    for target_user in target_users:
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


def get_verified_target_users(
    _enforce_fam_access_validated = Depends(enforce_fam_client_token),
    requester: RequesterSchema = Depends(get_current_requester),
    target_users: list[TargetUserSchema] = Depends(get_target_users_from_ids),
    role: FamRole = Depends(get_request_role_from_id),
) -> TargetUserValidationResultSchema:
    """
    Validate a list of target users by calling IDIM web service, and update business Guid for the found BCeID users.
    Returns a list of verified TargetUserSchema objects. Raises on any invalid user.
    """
    return validate_target_users(requester, target_users, role)


async def enforce_bceid_by_same_org_guard(
    _enforce_fam_access_validated = Depends(enforce_fam_client_token),
    _enforce_user_type_auth: None = Depends(authorize_by_user_type),
    requester: RequesterSchema = Depends(get_current_requester),
    target_users: list[TargetUserSchema] = Depends(get_target_users_from_ids),
    role: FamRole = Depends(get_request_role_from_id),
):
    """
    Router guard to enforce BCeID same organization validation.

    This guard ensures that a BCeID user (requester) can only manage users from the same organization.
    It validates the organization consistency between the requester and the target users.
    Additionally, it ensures that all target users are verified before enforcing the organization rule.

    - For IDIR requester, there is no need to get "verified target user" as IDIR user can remove any IDIR user
      and any BCeID user.

    Parameters:
        _enforce_fam_access_validated: Dependency to validate the FAM client token.
        _enforce_user_type_auth: Dependency to authorize user type.
        requester: The user making the request, validated as the current requester.
        target_users: List of target users to be managed.
        role: The application role context for the validation.

    Raises:
        HTTPException: If the requester and target users are not from the same organization.
        HTTPException: If there are failed target users during validation.
    """
    LOGGER.debug(
        f"Verifying requester {requester.user_name} (type {requester.user_type_code}) "
        "is allowed to manage BCeID target users for the same organization."
    )

    if requester.user_type_code == UserType.BCEID:
        # Verify target users before enforcing organization rule
        validation_result = validate_target_users(requester, target_users, role)

        # Raise an error if there are failed users
        if validation_result.failed_users:
            app_name = role.application.application_name
            failed_usernames = [user.user_name for user in validation_result.failed_users]
            error_msg = f"Unable to verify the following users: {failed_usernames}. Please contact {app_name} administrator for the action."
            utils.raise_http_exception(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                error_code=ERROR_CODE_UNKNOWN_STATE,
                error_msg=error_msg,
            )

        # Enforce same organization rule on verified users
        try:
            validate_bceid_same_org(requester, validation_result.verified_users)
        except Exception as e:
            utils.raise_http_exception(
                status_code=HTTPStatus.FORBIDDEN,
                error_code=ERROR_CODE_DIFFERENT_ORG_GRANT_PROHIBITED,
                error_msg=f"An error occurred while validating organization consistency: {str(e)}",
            )


def enforce_bceid_terms_conditions_guard(
    _enforce_fam_access_validated = Depends(enforce_fam_client_token),
    requester: RequesterSchema = Depends(get_current_requester),
):
    if requester.requires_accept_tc:
        utils.raise_http_exception(
            error_code=ERROR_CODE_TERMS_CONDITIONS_REQUIRED,
            error_msg="Requires to accept terms and conditions.",
        )


def verify_api_key_for_update_user_info(x_api_key: str = Security(x_api_key)):
    if x_api_key != config.get_api_key_for_update_user_info():
        utils.raise_http_exception(
            status_code=HTTPStatus.UNAUTHORIZED,
            error_msg="Request needs api key.",
        )


def authorize_ext_api_by_app_role(
    requester: RequesterSchema = Depends(get_current_requester),
    app_client_id: str = Depends(get_request_app_client_id),
    db: Session = Depends(database.get_db),
) -> FamApplicationSchema:
    """
    This method is used for the external api authorization check.
    The requester must have the permission to call the external api for the application.
    """
    application: FamApplicationSchema = crud_application.get_application_by_app_client_id(db, app_client_id)
    if not application:
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_CODE_INVALID_OPERATION,
            error_msg=f"Token contains invalid application client id {utils.mask_string(app_client_id, 5)}",
        )

    has_call_api_permission: bool = crud_utils.allow_ext_call_api_permission(
        db, application.application_id, requester.user_name
    )
    if not has_call_api_permission:
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ERROR_PERMISSION_REQUIRED,
            error_msg="No permission to call the external API.",
        )

    return application