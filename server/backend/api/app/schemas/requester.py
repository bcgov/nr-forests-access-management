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
    # The user identity fields below are optional because a service-account
    # (client-credentials / machine-to-machine) token carries no user. For a user
    # token they are always populated from the FamUser record as before.
    user_name: Optional[
        Annotated[str, StringConstraints(max_length=USER_NAME_MAX_LEN)]
    ] = None
    first_name: Optional[
        Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    ] = None
    last_name: Optional[
        Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    ] = None
    email: Optional[Annotated[str, StringConstraints(max_length=EMAIL_MAX_LEN)]] = None
    # "B"(BCeID) or "I"(IDIR). It is the IDP provider.
    user_type_code: Union[UserType, None] = None
    user_guid: Optional[
        Annotated[str, StringConstraints(min_length=32, max_length=32)]
    ] = None
    business_guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    user_id: Optional[int] = None

    # belows are custom Requester information attributes.
    access_roles: Union[
        List[Annotated[str, StringConstraints(max_length=50)]], None
    ] = None
    is_delegated_admin: bool = False  # is delegated admin of any application
    requires_accept_tc: bool = False  # requires to accept terms and conditions

    # Service-account (machine-to-machine) attributes. When is_service_account is True
    # there is no user identity; the caller is identified by service_account_client_id.
    is_service_account: bool = False
    service_account_client_id: Optional[str] = None

    def is_external_delegated_admin(self):
        return self.user_type_code == UserType.BCEID and self.is_delegated_admin

    def log_identity(self) -> str:
        """Human-readable caller identity for logging (user vs service account)."""
        if self.is_service_account:
            return f"service-account client_id={self.service_account_client_id}"
        return f"user_name={self.user_name} (id={self.user_id})"

    model_config = ConfigDict(from_attributes=True)
