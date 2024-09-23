from typing import List, Optional, Union

from api.app.constants import (EMAIL_MAX_LEN, FIRST_NAME_MAX_LEN,
                               LAST_NAME_MAX_LEN, USER_NAME_MAX_LEN, UserType)
from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated


class RequesterSchema(BaseModel):
    """
    Class holding information for user who access FAM system after being
    authenticated. Logged on user with jwt token is parsed into Requester.
    It is transformed from db model "FamUser". Most endpoints will need this
    Requester instance, and can be available for router handler and passed to
    service layer.
    """

    # cognito_user_id => Cognito OIDC access token maps this to: username (ID token => "custom:idp_name" )
    cognito_user_id: Union[str, None] = None
    user_name: Annotated[str, StringConstraints(max_length=USER_NAME_MAX_LEN)]
    first_name: Optional[
        Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    ] = None
    last_name: Optional[
        Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    ] = None
    email: Optional[Annotated[str, StringConstraints(max_length=EMAIL_MAX_LEN)]] = None
    # "B"(BCeID) or "I"(IDIR). It is the IDP provider.
    user_type_code: Union[UserType, None] = None
    user_guid: Annotated[str, StringConstraints(min_length=32, max_length=32)]
    business_guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    user_id: int

    # belows are custom Requester information attributes.
    access_roles: Union[
        List[Annotated[str, StringConstraints(max_length=50)]], None
    ] = None
    is_delegated_admin: bool = False  # is delegated admin of any application
    requires_accept_tc: bool = False  # requires to accept terms and conditions

    def is_external_delegated_admin(self):
        return self.user_type_code == UserType.BCEID and self.is_delegated_admin

    model_config = ConfigDict(from_attributes=True)
