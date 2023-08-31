import logging
from http import HTTPStatus

from api.app import database
from api.app.crud import crud_application, crud_role, crud_user, crud_user_role
from api.app.jwt_validation import (ERROR_PERMISSION_REQUIRED,
                                    get_access_roles,
                                    get_request_cognito_user_id,
                                    validate_token)
from api.app.models.model import FamRole, FamUser, FamUserType
from api.app.schemas import Requester
from fastapi import Depends, HTTPException, Request
from requests import JSONDecodeError
from sqlalchemy.orm import Session

"""
This file is intended to host functions only to guard the endpoints at framework's
router level BEFORE reaching withint the router logic (They should not be used
at service layer).
"""

LOGGER = logging.getLogger(__name__)

ERROR_INVALID_APPLICATION_ID = "invalid_application_id"
ERROR_INVALID_ROLE_ID = "invalid_role_id"
ERROR_REQUESTER_NOT_EXISTS = "requester_not_exists"
ERROR_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"

no_requester_exception = HTTPException(
    status_code=HTTPStatus.FORBIDDEN, # 403
    detail={
        "code": ERROR_REQUESTER_NOT_EXISTS,
        "description": "Requester does not exist, action is not allowed",
    }
)

external_user_prohibited_exception = HTTPException(
    status_code=HTTPStatus.FORBIDDEN, # 403
    detail={
        "code": ERROR_EXTERNAL_USER_ACTION_PROHIBITED,
        "description": "Action is not allowed for external user.",
    }
)

def authorize_by_app_id(
    application_id,
    db: Session = Depends(database.get_db),
    claims: dict = Depends(validate_token)
):
    application = crud_application.get_application(application_id=application_id, db=db)
    if not application:
        raise HTTPException(
            status_code=403,
            detail={
                "code": ERROR_INVALID_APPLICATION_ID,
                "description": f"Application ID {application_id} not found",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    required_role = f"{application.application_name.upper()}_ACCESS_ADMIN"
    access_roles = get_access_roles(claims)

    if required_role not in access_roles:
        raise HTTPException(
            status_code=403,
            detail={
                "code": ERROR_PERMISSION_REQUIRED,
                "description": f"Operation requires role {required_role}",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_request_role_from_id(
        request: Request,
        db: Session = Depends(database.get_db)
) -> FamRole:
    """
    (this is a sub-dependency as convenient function)
    To get role id from request...
    Some endpoints has path_params with "user_role_xref_id".
    Some endpoints has role_id in request body.
    """
    user_role_xref_id = None
    if "user_role_xref_id" in request.path_params:
        user_role_xref_id = request.path_params["user_role_xref_id"]

    if (user_role_xref_id):
        LOGGER.debug(f"Retrieving role by user_role_xref_id: "
                     f"{user_role_xref_id}")
        user_role = crud_user_role.find_by_id(db, user_role_xref_id)
        return user_role.role

    else:
        try:
            rbody = await request.json()
            LOGGER.debug(f"Try retrieving role by Request's role_id:"
                         f"{user_role_xref_id}")
            role = crud_role.get_role(db, rbody["role_id"])
            return role # role could be None.

        except JSONDecodeError:
            return None


def authorize_by_application_role(
    # Depends on "get_request_role_from_id()" to figure out
    # what id to use to get role from endpoint.
    role: FamRole = Depends(get_request_role_from_id),
    db: Session = Depends(database.get_db),
    claims: dict = Depends(validate_token),
):
    """
    This router validation is currently design to validate logged on "admin"
    has authority to perform actions for application with roles in [app]_ACCESS_ADMIN.
    This function basically is the same and depends on (authorize_by_app_id()) but for
    the need that some routers contains target role_id in the request (instead of application_id).
    """
    if not role:
        raise HTTPException(
            status_code=403,
            detail={
                "code": ERROR_INVALID_ROLE_ID,
                "description": f"Requester has no appropriate role.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    authorize_by_app_id(
        application_id=role.application_id,
        db=db,
        claims=claims
    )
    return role


async def get_current_requester(
    request_cognito_user_id: str = Depends(get_request_cognito_user_id),
    access_roles = Depends(get_access_roles),
    db: Session = Depends(database.get_db)
):
    fam_user: FamUser = crud_user.get_user_by_cognito_user_id(db, request_cognito_user_id)
    if fam_user is None:
        raise no_requester_exception

    requester = Requester.from_orm(fam_user)
    requester.access_roles = access_roles
    LOGGER.debug(f"Current request user (requester): {requester}")
    return requester


async def internal_only_action(
    requester: Requester =Depends(get_current_requester)
):
    if requester.user_type_code is not FamUserType.USER_TYPE_IDIR:
        raise external_user_prohibited_exception


# def enforce_self_grant_guard(
#     db: Session = Depends(database.get_db),
#     requester: Requester = Depends(get_current_requester)
# ):
#     pass