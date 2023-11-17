import logging
from typing import List, Optional, Union

from pydantic import StringConstraints, ConfigDict, BaseModel

from . import constants as famConstants
from typing_extensions import Annotated

LOGGER = logging.getLogger(__name__)


# Schema classes Requester and TargetUser are for backend system used and
# NOT intended as part of the request/respoinse body in the endpoint. Logged
# on user with jwt token is parsed into Requester (before route handler).
# Same as other Schema classes, it can be transformed from db model.
class Requester(BaseModel):
    """
    Class holding information for user who access FAM system after authenticated.
    """

    # cognito_user_id => Cognito OIDC access token maps this to: username (ID token => "custom:idp_name" )
    cognito_user_id: Union[str, None] = None
    user_name: Annotated[str, StringConstraints(max_length=15)]
    # "B"(BCeID) or "I"(IDIR). It is the IDP provider.
    user_type_code: Union[famConstants.UserType, None] = None
    access_roles: Union[
        List[Annotated[str, StringConstraints(max_length=50)]], None
    ] = None

    model_config = ConfigDict(from_attributes=True)


class TargetUser(Requester):
    pass


class FamUser(BaseModel):
    user_type_code: famConstants.UserType
    cognito_user_id: Optional[
        Annotated[str, StringConstraints(max_length=100)]
    ] = None  # temporarily optional
    user_name: Annotated[str, StringConstraints(max_length=100)]
    user_guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    create_user: Annotated[str, StringConstraints(max_length=60)]
    update_user: Optional[Annotated[str, StringConstraints(max_length=60)]] = None

    model_config = ConfigDict(from_attributes=True)


# Application Admin assignment with one application at a time for the user.
class FamAppAdminCreate(BaseModel):
    user_name: Annotated[
        str, StringConstraints(min_length=3, max_length=100)
    ]  # db max length
    user_type_code: famConstants.UserType
    application_id: int

    model_config = ConfigDict(from_attributes=True)


class FamAppAdminGet(BaseModel):
    application_admin_id: int
    application_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
