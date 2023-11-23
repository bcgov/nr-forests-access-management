import logging
from http import HTTPStatus
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Union
import json

from api.app import database
from api.app.jwt_validation import (
    ERROR_PERMISSION_REQUIRED,
    get_access_roles,
    get_request_cognito_user_id,
    validate_token,
)
from api.app.schemas import Requester, TargetUser, FamAppAdminCreate
from api.app.models.model import FamUser
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.user_service import UserService
from api.app.services.application_service import ApplicationService

LOGGER = logging.getLogger(__name__)


ERROR_SELF_GRANT_PROHIBITED = "self_grant_prohibited"
ERROR_INVALID_APPLICATION_ID = "invalid_application_id"
ERROR_INVALID_ROLE_ID = "invalid_role_id"
ERROR_REQUESTER_NOT_EXISTS = "requester_not_exists"
ERROR_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"
ERROR_INVALID_APPLICATION_ADMIN_ID = "invalid_application_admin_id"


no_requester_exception = HTTPException(
    status_code=HTTPStatus.FORBIDDEN,  # 403
    detail={
        "code": ERROR_REQUESTER_NOT_EXISTS,
        "description": "Requester does not exist, action is not allowed",
    },
)


def authorize_by_fam_admin(claims: dict = Depends(validate_token)):
    required_role = "FAM_ACCESS_ADMIN"
    access_roles = get_access_roles(claims)

    if required_role not in access_roles:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail={
                "code": ERROR_PERMISSION_REQUIRED,
                "description": f"Operation requires role {required_role}",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_requester(
    request_cognito_user_id: str = Depends(get_request_cognito_user_id),
    access_roles=Depends(get_access_roles),
    db: Session = Depends(database.get_db),
):
    user_service = UserService(db)
    fam_user: FamUser = user_service.get_user_by_cognito_user_id(
        request_cognito_user_id
    )
    if fam_user is None:
        raise no_requester_exception

    requester = Requester.model_validate(fam_user)
    requester.access_roles = access_roles
    LOGGER.debug(f"Current request user (requester): {requester}")
    return requester


# Note!!
# currently to take care of different scenarios (id or fields needed in path/param/body)
# to find target user, will only consider request "path_params" and for "body"(json) for PUT/POST.
# For now, only consider known cases ("router_application_admin.py" endpoints that need this).
# Specifically: "user_role_xref_id" and "user_name/user_type_code".
# Very likely in future might have "cognito_user_id" case.
async def get_target_user_from_id(
    request: Request, db: Session = Depends(database.get_db)
) -> Union[TargetUser, None]:
    """
    This is used as FastAPI sub-dependency to find target_user for guard purpose.
    For requester, use "get_current_requester()" above.
    """
    # from path_param - application_admin_id, when remove admin access for a user
    user_service = UserService(db)
    if "application_admin_id" in request.path_params:
        application_admin_service = ApplicationAdminService(db)
        application_admin = application_admin_service.get_application_admin_by_id(
            request.path_params["application_admin_id"]
        )
        return (
            TargetUser.model_validate(application_admin.user)
            if application_admin is not None
            else None
        )
    else:
        # from body - {user_name/user_type_code}, when grant admin access
        try:
            rbody = await request.json()
            user = user_service.get_user_by_domain_and_name(
                rbody["user_type_code"],
                rbody["user_name"],
            )
            return TargetUser.model_validate(user) if user is not None else None
        except json.JSONDecodeError:
            return None


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


async def require_exist_application_admin(
    application_admin_id: int, db: Session = Depends(database.get_db)
):
    application_admin_service = ApplicationAdminService(db)
    application_admin = application_admin_service.get_application_admin_by_id(
        application_admin_id
    )
    if not application_admin:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={
                "code": ERROR_INVALID_APPLICATION_ADMIN_ID,
                "description": f"Application Admin ID {application_admin_id} not found",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_exist_application(
    application_admin_request: FamAppAdminCreate, db: Session = Depends(database.get_db)
):
    application_service = ApplicationService(db)
    application = application_service.get_application(
        application_admin_request.application_id
    )
    if not application:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={
                "code": ERROR_INVALID_APPLICATION_ID,
                "description": f"Application ID {application_admin_request.application_id} not found",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
