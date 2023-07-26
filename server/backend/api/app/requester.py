
import logging
from typing import List, Union

from api.app import database, jwt_validation
from api.app.crud import crud_user
from api.app.models.model import FamUser, FamUserType
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)

ERROR_REQUESTER_NOT_EXISTS = "requester_not_exists"
ERROR_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"

no_requester_exception = HTTPException(
    status_code=403,
    detail={
        "code": ERROR_REQUESTER_NOT_EXISTS,
        "description": "Requester does not exist, action is not allowed",
    }
)

external_user_prohibited_exception = HTTPException(
    status_code=403,
    detail={
        "code": ERROR_EXTERNAL_USER_ACTION_PROHIBITED,
        "description": "Action is not allowed for external user.",
    }
)

class Requester(BaseModel):
    """
    Class holding information for user who access FAM system after authenticated.
    """
    # cognito_user_id => Cognito OIDC access token maps this to: username (ID token => "custom:idp_name" )
    cognito_user_id: Union[str, None]
    user_name: str
    # "B"(BCeID) or "I"(IDIR). It is the IDP provider.
    user_type: Union[str, None]
    access_roles: Union[List[str], None]


async def get_current_requester(
    request_cognito_username: str = Depends(jwt_validation.get_request_cognito_username),
    access_roles = Depends(jwt_validation.get_access_roles),
    db: Session = Depends(database.get_db)
):
    # TODO: verify if it is good idea to get user from db or exchange ID Token with Cognito is better.
    famUser: FamUser = crud_user.get_user_by_cognito_user_id(db, request_cognito_username)
    if famUser is None:
        raise no_requester_exception

    return Requester(**{
        "cognito_user_id": request_cognito_username,
        "user_name": famUser.user_name,
        "user_type": famUser.user_type_code,
        "access_roles": access_roles
    })


async def internal_only_action(
    requester=Depends(get_current_requester)
):
    if requester.user_type is not FamUserType.USER_TYPE_IDIR:
        raise external_user_prohibited_exception