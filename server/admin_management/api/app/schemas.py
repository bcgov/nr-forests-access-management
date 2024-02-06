import logging
from typing import List, Optional, Union
from pydantic import StringConstraints, ConfigDict, BaseModel, Field

from . import constants as famConstants
from typing_extensions import Annotated

LOGGER = logging.getLogger(__name__)

# This schema file uses the following convention on sechema objects:
# - If the object is used for router's request/response BODY, then the class name would be:
#      [SomeClassName]Request or [SomeClassName]Response
# - If the object does not involve with router's request/response BODY, then the class name would be:
#      [SomeClassName]Dto (DTO object, some cases naming as "CreateDto" but not necessarily)
# - Exception (some cases are flexible):
#   Requester, TargetUser and some "Base" class, such as "FamApplicationBase"


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

    # This is the fam_user.user_id (primary key in fam_user table). When JWT token is validated based on above
    # "cognito_user_id" (external linking piece for logged on user to AWS Cognito) This "Requester" is retrieved
    # from datbase and the user record will contain this user_id; and also is the reference-id from other database
    # entities (e.g., app_fam.fam_application_admin, app_fam.fam_access_control_privilege)
    user_id: Optional[int] = None
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


class FamApplicationGetResponse(FamApplicationBase):
    application_id: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------- FAM User --------------------------------------- #
class FamUserBase(BaseModel):
    user_name: Annotated[str, StringConstraints(max_length=20)]

    model_config = ConfigDict(from_attributes=True)


class FamUserDto(FamUserBase):
    user_type_code: famConstants.UserType
    create_user: Annotated[str, StringConstraints(max_length=60)]

    model_config = ConfigDict(from_attributes=True)


class FamUserTypeDto(BaseModel):
    user_type_code: famConstants.UserType = Field(alias="code")
    description: Annotated[str, StringConstraints(max_length=35)]

    # required to set populate_by_name for alias fields
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FamUserInfoDto(FamUserBase):
    user_type_relation: FamUserTypeDto = Field(alias="user_type")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ----------------------------------- FAM Forest Client ------------------------------------ #
class FamForestClientBase(BaseModel):
    # Note, the request may contain string(with leading '0')
    forest_client_number: Annotated[str, StringConstraints(max_length=8)]

    model_config = ConfigDict(from_attributes=True)


class FamForestClientCreateDto(FamForestClientBase):
    create_user: Annotated[str, StringConstraints(max_length=60)]

    model_config = ConfigDict(from_attributes=True)


class FamForestClientStatusDto(BaseModel):
    status_code: famConstants.FamForestClientStatusType
    description: Annotated[str, StringConstraints(max_length=10)]

    model_config = ConfigDict(from_attributes=True)


class FamForestClientDto(FamForestClientBase):
    client_name: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    status: Optional[FamForestClientStatusDto] = None

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------- FAM Role ------------------------------------------- #
class FamRoleBase(BaseModel):
    role_name: Annotated[str, StringConstraints(max_length=100)]
    role_type_code: famConstants.RoleType

    model_config = ConfigDict(from_attributes=True)


class FamRoleCreateDto(FamRoleBase):
    application_id: int = Field(title="Application this role is associated with")
    role_purpose: Optional[Annotated[str, StringConstraints(max_length=200)]] = None
    parent_role_id: Union[int, None] = Field(
        default=None, title="Reference role_id to higher role"
    )
    forest_client_number: Optional[Annotated[str, StringConstraints(max_length=8)]] = (
        Field(default=None, title="Forest Client this role is associated with")
    )
    create_user: Annotated[str, StringConstraints(max_length=60)]
    client_number: Optional[FamForestClientCreateDto] = (
        None  # this is matched with the model
    )

    model_config = ConfigDict(from_attributes=True)


class FamRoleWithClientDto(BaseModel):
    role_id: int
    role_name: Annotated[str, StringConstraints(max_length=100)]
    client_number: Optional[FamForestClientBase] = None
    parent_role: Optional[FamRoleBase] = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------- FAM Application Admin ----------------------------------- #
# Application Admin assignment with one application at a time for the user.
class FamAppAdminCreateRequest(BaseModel):
    user_name: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    user_type_code: famConstants.UserType
    application_id: int

    model_config = ConfigDict(from_attributes=True)


class FamAppAdminGetResponse(BaseModel):
    application_admin_id: int
    user_id: int
    application_id: int
    user: FamUserInfoDto
    application: FamApplicationBase

    model_config = ConfigDict(from_attributes=True)


# -------------------------- FAM Access Control Privilege (Delegated Admin) -------------------------- #
class FamAccessControlPrivilegeCreateRequest(BaseModel):
    """
    This is used at router level, the data we receive from frontend.
    Use username and user_type_code to get user_id,
    and for concrete role, can use its role_id directly,
    but for abstract role, need to create/get child role_id based on the forest client number,
    and then use schema FamAccessControlPrivilegeCreateDto to insert into the database
    """

    user_name: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    user_type_code: famConstants.UserType
    role_id: int
    forest_client_numbers: Union[
        List[Annotated[str, StringConstraints(min_length=1, max_length=8)]], None
    ] = None

    model_config = ConfigDict(from_attributes=True)


class FamAccessControlPrivilegeCreateDto(BaseModel):
    """
    This is used at repository level, pass to the database to create the record
    """

    user_id: int
    create_user: Annotated[str, StringConstraints(max_length=60)]
    role_id: int

    model_config = ConfigDict(from_attributes=True)


class FamAccessControlPrivilegeGetResponse(BaseModel):
    access_control_privilege_id: int
    user_id: int
    role_id: int
    user: FamUserInfoDto
    role: FamRoleWithClientDto

    model_config = ConfigDict(from_attributes=True)


class FamAccessControlPrivilegeCreateResponse(BaseModel):
    status_code: int
    detail: FamAccessControlPrivilegeGetResponse
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------- FAM Admin User Access ---------------------------------------- #
class FamApplicationDto(BaseModel):
    id: int = Field(validation_alias="application_id")
    name: Annotated[str, StringConstraints(max_length=100)] = Field(
        validation_alias="application_name"
    )
    description: Annotated[Optional[str], StringConstraints(max_length=200)] = Field(
        default=None, validation_alias="application_description"
    )
    env: Optional[famConstants.AppEnv] = Field(
        validation_alias="app_environment", default=None
    )

    model_config = ConfigDict(from_attributes=True)


class FamRoleDto(BaseModel):
    # Note, this "id" for role can either be concrete role's or abstract role's id.
    # In abstract role with this id, forest_clients should be present.
    id: int = Field(validation_alias="role_id")
    name: Annotated[str, StringConstraints(max_length=100)] = Field(
        validation_alias="role_name"
    )
    type_code: famConstants.RoleType = Field(validation_alias="role_type_code")
    forest_clients: Optional[List[str]] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


class FamGrantDetailDto(BaseModel):
    application: FamApplicationDto
    roles: Optional[List[FamRoleDto]] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


class FamAuthGrantDto(BaseModel):
    auth_key: famConstants.AdminRoleAuthGroup
    grants: List[FamGrantDetailDto]

    model_config = ConfigDict(from_attributes=True)


class AdminUserAccessResponse(BaseModel):
    access: List[FamAuthGrantDto]

    model_config = ConfigDict(from_attributes=True)
