import logging
from typing import List, Optional, Union
from pydantic import StringConstraints, ConfigDict, BaseModel, Field

from . import constants as famConstants
from typing_extensions import Annotated

LOGGER = logging.getLogger(__name__)


# -------------------------------------- Requester --------------------------------------- #
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
    user_name: Annotated[str, StringConstraints(max_length=20)]
    # "B"(BCeID) or "I"(IDIR). It is the IDP provider.
    user_type_code: Union[famConstants.UserType, None] = None
    access_roles: Union[
        List[Annotated[str, StringConstraints(max_length=50)]], None
    ] = None

    model_config = ConfigDict(from_attributes=True)


class TargetUser(Requester):
    pass


# -------------------------------------- FAM Application --------------------------------------- #
class FamApplicationBase(BaseModel):
    application_name: Annotated[str, StringConstraints(max_length=100)]
    application_description: Annotated[str, StringConstraints(max_length=200)]
    app_environment: Optional[famConstants.AppEnv] = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------- FAM User --------------------------------------- #
class FamUserBase(BaseModel):
    user_type_code: famConstants.UserType
    user_name: Annotated[str, StringConstraints(max_length=20)]

    model_config = ConfigDict(from_attributes=True)


class FamUserCreate(FamUserBase):
    create_user: Annotated[str, StringConstraints(max_length=60)]

    model_config = ConfigDict(from_attributes=True)


class FamUserType(BaseModel):
    user_type_code: famConstants.UserType = Field(alias="code")
    description: Annotated[str, StringConstraints(max_length=35)]

    # required to set populate_by_name for alias fields
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FamUserInfo(FamUserBase):
    user_type_relation: FamUserType = Field(alias="user_type")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ----------------------------------- FAM Forest Client ------------------------------------ #
class FamForestClientCreate(BaseModel):
    # Note, the request may contain string(with leading '0')
    forest_client_number: Annotated[str, StringConstraints(max_length=8)]
    # client_name: str
    create_user: Annotated[str, StringConstraints(max_length=60)]

    model_config = ConfigDict(from_attributes=True)


class FamForestClientStatus(BaseModel):
    status_code: famConstants.FamForestClientStatusType
    description: Annotated[str, StringConstraints(max_length=10)]

    model_config = ConfigDict(from_attributes=True)


class FamForestClient(BaseModel):
    client_name: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    forest_client_number: Annotated[str, StringConstraints(max_length=8)]
    status: Optional[FamForestClientStatus] = None

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------- FAM Role ------------------------------------------- #
class FamRoleMin(BaseModel):
    role_name: Annotated[str, StringConstraints(max_length=100)]
    role_type_code: famConstants.RoleType
    application_id: int = Field(title="Application this role is associated with")

    model_config = ConfigDict(from_attributes=True)


class FamRoleCreate(FamRoleMin):
    role_purpose: Union[Annotated[str, StringConstraints(max_length=200)], None] = None
    parent_role_id: Union[int, None] = Field(
        default=None, title="Reference role_id to higher role"
    )
    forest_client_number: Union[
        Annotated[str, StringConstraints(max_length=8)], None
    ] = Field(default=None, title="Forest Client this role is associated with")
    create_user: Annotated[str, StringConstraints(max_length=60)]
    client_number: Optional[FamForestClientCreate] = None

    model_config = ConfigDict(from_attributes=True)


class FamRoleWithClient(BaseModel):
    role_id: int
    role_name: Annotated[str, StringConstraints(max_length=100)]
    client_number: Optional[FamForestClient] = None
    parent_role: Optional[FamRoleMin] = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------- FAM Application Admin ----------------------------------- #
# Application Admin assignment with one application at a time for the user.
class FamAppAdminCreate(BaseModel):
    user_name: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    user_type_code: famConstants.UserType
    application_id: int

    model_config = ConfigDict(from_attributes=True)


class FamAppAdminGet(BaseModel):
    application_admin_id: int
    user_id: int
    application_id: int
    user: FamUserInfo
    application: FamApplicationBase

    model_config = ConfigDict(from_attributes=True)


# -------------------------- FAM Access Control Privilege (Delegated Admin) -------------------------- #
class FamAccessControlPrivilegeCreate(BaseModel):
    user_name: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    user_type_code: famConstants.UserType
    role_id: int
    forest_client_number: Union[
        List[Annotated[str, StringConstraints(min_length=1, max_length=8)]], None
    ] = None

    model_config = ConfigDict(from_attributes=True)


class FamAccessControlPrivilegeGet(BaseModel):
    access_control_privilege_id: int
    user_id: int
    role_id: int
    user: FamUserInfo
    role: FamRoleWithClient

    model_config = ConfigDict(from_attributes=True)


class FamAccessControlPrivilegeCreateResponse(BaseModel):
    status_code: int
    detail: FamAccessControlPrivilegeGet
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
