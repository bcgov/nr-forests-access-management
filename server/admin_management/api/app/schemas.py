import logging
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing_extensions import Annotated

from . import constants as famConstants

LOGGER = logging.getLogger(__name__)

# This schema file uses the following convention on sechema objects:
# - If the object is used for router's request/response BODY, then the class name would be:
#      [SomeClassName]Request or [SomeClassName]Response
# - If the object does not involve with router's request/response BODY, then the class name would be:
#      [SomeClassName]Dto (DTO object, some cases naming as "CreateDto" but not necessarily)
# - Exception (some cases are flexible):
#   Requester, TargetUser and some "Base" class, such as "FamApplicationBase"


# -------------------------------------- Requester and TargetUser --------------------------------------- #
"""
The "Requester" and "TargetUser" schema objects are internal backend system
wide objects.
They are "NOT" intended as part of the request/respoinse body for endponts.
The "Requester" means "who" is issueing the request for one of FAM endpoints.
The "TargetUser" means "who" is the user this endpoint request is targeting
for.
    - The exsiting endpoints so far only target on one target user. It might be
      possible some endpoints will target on multiple users. In such case,
      further design or refactoring might be needed.
"""


class Requester(BaseModel):
    """
    Class holding information for user who access FAM system after being
    authenticated. Logged on user with jwt token is parsed into Requester.
    It is transformed from db model "FamUser". Most endpoints will need this
    Requester instance, and can be available for router handler and passed to
    service layer.
    """

    # cognito_user_id => Cognito OIDC access token maps this to: username (ID token => "custom:idp_name" )
    cognito_user_id: Union[str, None] = None

    # This is the fam_user.user_id (primary key in fam_user table). When JWT token is validated based on above
    # "cognito_user_id" (external linking piece for logged on user to AWS Cognito) This "Requester" is retrieved
    # from datbase and the user record will contain this user_id; and also is the reference-id from other database
    # entities (e.g., app_fam.fam_application_admin, app_fam.fam_access_control_privilege)
    user_id: int
    user_guid: Annotated[str, StringConstraints(min_length=32, max_length=32)]
    business_guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    user_name: Annotated[str, StringConstraints(min_length=2, max_length=20)]
    # "B"(BCeID) or "I"(IDIR). It is the IDP provider.
    user_type_code: famConstants.UserType
    access_roles: Union[
        List[Annotated[str, StringConstraints(max_length=50)]], None
    ] = None

    model_config = ConfigDict(from_attributes=True)


class TargetUser(Requester):
    """
    Inherit from the class "Requester". Same as Requester, the TargetUser can
    be transformed from FamUser db model. However, for new user, the
    information will not be available from db model. In such case, some
    properties will be set from the request parameters or request body.
    Meethod that relys on TargetUser might need to check if it is a new user by
    checking "is_new_user()".
    """
    user_id: Optional[int] = None
    first_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None


# -------------------------------------- FAM Application --------------------------------------- #
class FamApplicationBase(BaseModel):
    application_name: Annotated[str, StringConstraints(max_length=100)]
    application_description: Annotated[str, StringConstraints(max_length=200)]
    app_environment: Optional[famConstants.AppEnv] = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------- FAM User --------------------------------------- #
class FamUserBase(BaseModel):
    user_name: Annotated[str, StringConstraints(max_length=20)]

    model_config = ConfigDict(from_attributes=True)


class FamUserDto(FamUserBase):
    user_type_code: famConstants.UserType
    user_guid: Annotated[str, StringConstraints(min_length=32, max_length=32)]
    create_user: Annotated[str, StringConstraints(max_length=100)]

    model_config = ConfigDict(from_attributes=True)


class FamUserTypeDto(BaseModel):
    user_type_code: famConstants.UserType = Field(alias="code")
    description: Annotated[str, StringConstraints(max_length=35)]

    # required to set populate_by_name for alias fields
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FamUserInfoDto(FamUserBase):
    user_type_relation: FamUserTypeDto = Field(alias="user_type")
    first_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ----------------------------------- FAM Forest Client ------------------------------------ #
class FamForestClientBase(BaseModel):
    # Note, the request may contain string(with leading '0')
    forest_client_number: Annotated[str, StringConstraints(max_length=8)]

    model_config = ConfigDict(from_attributes=True)


class FamForestClientCreateDto(FamForestClientBase):
    create_user: Annotated[str, StringConstraints(max_length=100)]

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------- FAM Role ------------------------------------------- #
class FamRoleBase(BaseModel):
    role_name: Annotated[str, StringConstraints(max_length=100)]
    role_type_code: famConstants.RoleType

    model_config = ConfigDict(from_attributes=True)


class FamRoleCreateDto(FamRoleBase):
    application_id: int = Field(title="Application this role is associated with")
    role_purpose: Optional[Annotated[str, StringConstraints(max_length=300)]] = None
    parent_role_id: Union[int, None] = Field(
        default=None, title="Reference role_id to higher role"
    )
    forest_client_number: Optional[Annotated[str, StringConstraints(max_length=8)]] = (
        Field(default=None, title="Forest Client this role is associated with")
    )
    create_user: Annotated[str, StringConstraints(max_length=100)]
    client_number: Optional[FamForestClientCreateDto] = (
        None  # this is matched with the model
    )

    model_config = ConfigDict(from_attributes=True)


class FamRoleWithClientDto(BaseModel):
    role_id: int
    role_name: Annotated[str, StringConstraints(max_length=100)]
    client_number: Optional[FamForestClientBase] = None
    parent_role: Optional[FamRoleBase] = None
    application: FamApplicationBase

    model_config = ConfigDict(from_attributes=True)


# -------------------------------- FAM Application Admin ----------------------------------- #
# Application Admin assignment with one application at a time for the user.
class FamAppAdminCreateRequest(BaseModel):
    user_name: Annotated[str, StringConstraints(min_length=3, max_length=20)]
    user_guid: Annotated[str, StringConstraints(min_length=32, max_length=32)]
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
    user_guid: Annotated[str, StringConstraints(min_length=32, max_length=32)]
    user_type_code: famConstants.UserType
    role_id: int
    forest_client_numbers: Union[
        List[Annotated[str, StringConstraints(min_length=1, max_length=8)]], None
    ] = None
    requires_send_user_email: bool = False

    model_config = ConfigDict(from_attributes=True)


class FamAccessControlPrivilegeCreateDto(BaseModel):
    """
    This is used at repository level, pass to the database to create the record
    """

    user_id: int
    create_user: Annotated[str, StringConstraints(max_length=100)]
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


class FamAccessControlPrivilegeResponse(BaseModel):
    email_sending_status: famConstants.EmailSendingStatus = famConstants.EmailSendingStatus.NOT_REQUIRED
    assignments_detail: List[FamAccessControlPrivilegeCreateResponse]


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
    description: Annotated[str, StringConstraints(max_length=300)] = Field(
        validation_alias="role_purpose"
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


# ------------------------------------- Forest Client API Integraion ---------------------------------------- #
class ForestClientIntegrationFindResponse(BaseModel):
    clientNumber: str
    clientName: str
    clientStatusCode: str
    clientTypeCode: str


# ------------------------------------- IDIM Proxy API Integraion ---------------------------------------- #
class IdimProxySearchParam(BaseModel):
    userId: Annotated[
        str, StringConstraints(max_length=20)
    ]  # param for Idim-Proxy search of this form (not snake case)


class IdimProxyBceidSearchParam(BaseModel):
    searchUserBy: famConstants.IdimSearchUserParamType
    searchValue: str


class IdimProxyIdirInfo(BaseModel):
    # property returned from Idim-Proxy search of this form (not snake case)
    found: bool
    userId: Annotated[str, StringConstraints(max_length=20)]
    guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    firstName: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    lastName: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None


class IdimProxyBceidInfo(BaseModel):
    found: bool
    userId: Annotated[str, StringConstraints(max_length=20)]
    guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    businessGuid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    businessLegalName: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    firstName: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    lastName: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None


# ------------------------------------- GC Notify Integraion ---------------------------------------- #
class GCNotifyGrantDelegatedAdminEmailParam(BaseModel):
    send_to_email_address: EmailStr
    application_name: Annotated[str, StringConstraints(max_length=100)]
    first_name: Annotated[str, StringConstraints(max_length=20)]
    last_name: Annotated[str, StringConstraints(max_length=20)]
    role_list_string: Annotated[str, StringConstraints(max_length=200)]
    application_team_contact_email: Optional[EmailStr] = None

