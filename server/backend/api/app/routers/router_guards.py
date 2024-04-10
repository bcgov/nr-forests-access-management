import array
import json
import logging
from http import HTTPStatus
from typing import Union

from api.app import database
from api.app.constants import UserType, RoleType
from api.app.crud import (
    crud_application,
    crud_role,
    crud_user,
    crud_user_role,
    crud_access_control_privilege,
)
from api.app.jwt_validation import (
    ERROR_PERMISSION_REQUIRED,
    ERROR_GROUPS_REQUIRED,
    JWT_GROUPS_KEY,
    get_access_roles,
    get_request_cognito_user_id,
    validate_token,
)
from api.app.integration.idim_proxy import IdimProxyService
from api.app.models.model import FamRole, FamUser
from api.app.schemas import IdimProxySearchParam, Requester, TargetUser
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

"""
This file is intended to host functions only to guard the endpoints at framework's
router level BEFORE reaching withint the router logic (They should not be used
at crud(service) layer).
"""

LOGGER = logging.getLogger(__name__)

ERROR_SELF_GRANT_PROHIBITED = "self_grant_prohibited"
ERROR_INVALID_APPLICATION_ID = "invalid_application_id"
ERROR_INVALID_ROLE_ID = "invalid_role_id"
ERROR_REQUESTER_NOT_EXISTS = "requester_not_exists"
ERROR_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"
ERROR_REQUEST_INVALID = "invalid_request"
ERROR_DIFFERENT_ORG_GRANT_PROHIBITED = "different_org_grant_prohibited"
ERROR_MISSING_KEY_ATTRIBUTE = "missing_key_attribute"

no_requester_exception = HTTPException(
    status_code=HTTPStatus.FORBIDDEN,  # 403
    detail={
        "code": ERROR_REQUESTER_NOT_EXISTS,
        "description": "Requester does not exist, action is not allowed",
    },
)

external_user_prohibited_exception = HTTPException(
    status_code=HTTPStatus.FORBIDDEN,
    detail={
        "code": ERROR_EXTERNAL_USER_ACTION_PROHIBITED,
        "description": "Action is not allowed for external user.",
    },
)

different_org_grant_prohibited_exception = HTTPException(
    status_code=HTTPStatus.FORBIDDEN,
    detail={
        "code": ERROR_DIFFERENT_ORG_GRANT_PROHIBITED,
        "description": "Managing for different organization is not allowed.",
    },
    headers={"WWW-Authenticate": "Bearer"},
)

missing_key_attribute_error = HTTPException(
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,  # 500
    detail={
        "code": ERROR_MISSING_KEY_ATTRIBUTE,
        "description": "Operation encountered unexpected error.",
    },
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_requester(
    request_cognito_user_id: str = Depends(get_request_cognito_user_id),
    db: Session = Depends(database.get_db),
):
    fam_user: FamUser = crud_user.get_user_by_cognito_user_id(
        db, request_cognito_user_id
    )
    if fam_user is None:
        raise no_requester_exception

    requester = Requester.model_validate(fam_user)
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
        user_access_control_privilege = (
            crud_access_control_privilege.get_delegated_admin_by_user_id(
                db, requester.user_id
            )
        )
        # if user is not app admin and not delegated admin of any application, throw miss access group error
        if len(user_access_control_privilege) == 0:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": ERROR_GROUPS_REQUIRED,
                    "description": "At least one access group is required",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )


def authorize_by_app_id(
    application_id: int,
    db: Session = Depends(database.get_db),
    claims: dict = Depends(validate_token),
    requester: Requester = Depends(get_current_requester),
):
    """
    This authorize_by_app_id method is used for the authorization check of a specific application,
    we require user to be the app admin or delegated admin of the application
    """
    requester_is_app_admin = is_app_admin(application_id, db, claims)

    # if user is not application admin
    if not requester_is_app_admin:
        # check if user is application delegated admin
        user_access_control_privilege = (
            crud_access_control_privilege.get_delegated_admin_by_user_and_app_id(
                db, requester.user_id, application_id
            )
        )
        # if user is not app admin and not delegated admin of the application, throw permission error
        if not user_access_control_privilege:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail={
                    "code": ERROR_PERMISSION_REQUIRED,
                    "description": f"Requester has no appropriate access.",
                },
                headers={"WWW-Authenticate": "Bearer"},
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
        try:
            rbody = await request.json()
            role_id = rbody["role_id"]
            LOGGER.debug(f"Retrieving role by Request's role_id: {role_id}")
            role = crud_role.get_role(db, role_id)  # role could be None.
        except json.JSONDecodeError:  # When request does not contains body part.
            role = None

    if not role:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail={
                "code": ERROR_INVALID_ROLE_ID,
                "description": "Role does not exist or failed to get the role_id from request",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return role


def authorize_by_application_role(
    # Depends on "get_request_role_from_id()" to figure out
    # what id to use to get role from endpoint.
    role: FamRole = Depends(get_request_role_from_id),
    db: Session = Depends(database.get_db),
    claims: dict = Depends(validate_token),
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
        application_id=role.application_id, db=db, claims=claims, requester=requester
    )
    return role


async def authorize_by_privilege(
    request: Request,
    role: FamRole = Depends(get_request_role_from_id),
    db: Session = Depends(database.get_db),
    claims: dict = Depends(validate_token),
    requester: Requester = Depends(get_current_requester),
):
    """
    This authorize_by_privilege method is used for checking if the requester has the privilege to grant/remove access of the role.
    :param role: for remove access, it is the concrete role get by user_role_xref_id in the request params;
                 for grant access, it is the concrete role, or the parent role of an abstract role get by role_id in the request params
    """
    requester_is_app_admin = is_app_admin(role.application_id, db, claims)

    # if requester is not application admin, check if has the privilege to grant/remove access of the role
    if not requester_is_app_admin:
        # for remove access, role is what we get above from Depends(get_request_role_from_id)
        # for grant access, if the request params has forest_client_number, need to get the child role
        # the child role should already exist when the delegated admin has been created
        if "user_role_xref_id" not in request.path_params:
            rbody = await request.json()
            forest_client_number = rbody["forest_client_number"]
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

        user_access_control_privilege = None
        if role:
            user_access_control_privilege = crud_access_control_privilege.get_delegated_admin_by_user_id_and_role_id(
                db, requester.user_id, role.role_id
            )
        # if user has no privilege of the role, throw permission error
        if not user_access_control_privilege:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail={
                    "code": ERROR_PERMISSION_REQUIRED,
                    "description": f"Requester has no privilege to grant this access.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )


# Note!!
# currently to take care of different scenarios (id or fields needed in path/param/body)
# to find target user, will only consider request "path_params" and for "body"(json) for PUT/POST.
# For now, only consider known cases ("router_user_role_assigment.py" endpoints that need this).
# Specifically: "user_role_xref_id" and "user_name/user_type_code".
# Very likely in future might have "cognito_user_id" case.
async def get_target_user_from_id(
    request: Request, db: Session = Depends(database.get_db)
) -> Union[TargetUser, None]:
    """
    This is used as FastAPI sub-dependency to find target_user for guard purpose.
    For requester, use "get_current_requester()" above.
    """
    # from path_param - user_role_xref_id
    if "user_role_xref_id" in request.path_params:
        user_role = crud_user_role.find_by_id(
            db, request.path_params["user_role_xref_id"]
        )
        return (
            TargetUser.model_validate(user_role.user) if user_role is not None else None
        )
    else:
        # from request body - {user_name/user_type_code}
        try:
            rbody = await request.json()
            user = crud_user.get_user_by_domain_and_name(
                db,
                rbody["user_type_code"],
                rbody["user_name"],
            )
            return TargetUser.model_validate(user) if user is not None else None
        except json.JSONDecodeError:
            return None


async def authorize_by_user_type(
    request: Request,
    requester: Requester = Depends(get_current_requester),
    target_user: Union[TargetUser, None] = Depends(get_target_user_from_id),
):
    """
    This authorize_by_user_type method is used to forbidden business bceid user manage idir user's access
    """
    if requester.user_type_code == UserType.BCEID:
        target_user_type_code = None
        if target_user:
            # in the case of granting/removing access to an existing user
            target_user_type_code = target_user.user_type_code
        else:
            # in the case of granting access to a new user
            try:
                rbody = await request.json()
                target_user_type_code = rbody["user_type_code"]
            except json.JSONDecodeError:
                target_user_type_code = None

        if not target_user_type_code:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail={
                    "code": ERROR_REQUEST_INVALID,
                    "description": f"Failed to get the user type code from the request.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        if target_user_type_code == UserType.IDIR:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail={
                    "code": ERROR_PERMISSION_REQUIRED,
                    "description": f"Business BCEID requester has no privilege to grant this access to IDIR user.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )


async def internal_only_action(requester: Requester = Depends(get_current_requester)):
    if requester.user_type_code is not UserType.IDIR:
        raise external_user_prohibited_exception


async def enforce_self_grant_guard(
    requester: Requester = Depends(get_current_requester),
    target_user: Union[TargetUser, None] = Depends(get_target_user_from_id),
):
    """
    Verify logged on admin (requester):
        Self granting/removing privilege currently isn't allowed.
    """
    LOGGER.debug(f"enforce_self_grant_guard: requester - {requester}")
    LOGGER.debug(f"enforce_self_grant_guard: target_user - {target_user}")
    if target_user is not None:
        is_same_user_name = requester.user_name == target_user.user_name
        is_same_user_type_code = requester.user_type_code == target_user.user_type_code

        if is_same_user_name and is_same_user_type_code:
            LOGGER.debug(
                f"User '{requester.user_name}' should not "
                f"grant/remove permission privilege to self."
            )
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail={
                    "code": ERROR_SELF_GRANT_PROHIBITED,
                    "description": "Altering permission privilege to self is not allowed",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )


async def enforce_bceid_by_same_org_guard(
    request: Request,
    requester: Requester = Depends(get_current_requester),
    target_user: Union[TargetUser, None] = Depends(get_target_user_from_id),
):
    """
    When requester is a BCeID user, enforce requester can only manage
    target user from the same organization.
    """
    LOGGER.info(
        f"Verifying requester {requester.user_name} (type {requester.user_type_code}) "
        "is allowed to manage BCeID target user for the same organization."
    )
    if requester.user_type_code == UserType.BCEID:
        requester_business_guid = requester.business_guid
        target_user_business_guid = None

        if target_user:
            # target_user found, expect it to have business_guid
            target_user_business_guid = target_user.business_guid
        else:
            # target_user does not exist in FAM database (new user)
            # search the target user from IDIM proxy and get business_guid
            # todo: update to search by user_guid instead of user_name
            try:
                rbody = await request.json()
                target_user_business_guid = get_business_guid(
                    requester, rbody["user_name"]
                )

            except json.JSONDecodeError:
                target_user_business_guid = None

        if requester_business_guid is None or target_user_business_guid is None:
            error_description = f"{missing_key_attribute_error.detail['description']} Requester or target user business GUID is missing."
            missing_key_attribute_error.detail["description"] = error_description
            raise missing_key_attribute_error

        if requester_business_guid.upper() != target_user_business_guid.upper():
            raise different_org_grant_prohibited_exception


# ----------------------- helper functions -------------------- #
def is_app_admin(
    application_id: int,
    db: Session,
    claims: dict,
):
    application = crud_application.get_application(application_id=application_id, db=db)
    if not application:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail={
                "code": ERROR_INVALID_APPLICATION_ID,
                "description": f"Application ID {application_id} not found",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin_role = f"{application.application_name.upper()}_ADMIN"
    access_roles = get_access_roles(claims)

    if access_roles and admin_role in access_roles:
        return True
    return False


def get_business_guid(requester: Requester, user_id: str):
    LOGGER.debug(f"Searching for business guid for user: {user_id}")
    idim_proxy_api = IdimProxyService(requester)
    search_result = idim_proxy_api.search_business_bceid(
        IdimProxySearchParam(**{"userId": user_id})
    )
    business_guid = search_result.get("businessGuid")
    return business_guid
