import logging
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing_extensions import Annotated

from . import constants as famConstants

LOGGER = logging.getLogger(__name__)


# --------------------------------- FAM Application --------------------------------- #
class FamApplication(BaseModel):
    application_id: int
    application_name: Annotated[str, StringConstraints(max_length=100)]
    application_description: Annotated[str, StringConstraints(max_length=200)]

    model_config = ConfigDict(from_attributes=True)


# --------------------------------- FAM User --------------------------------- #
class FamUser(BaseModel):
    user_type_code: famConstants.UserType
    cognito_user_id: Optional[Annotated[str, StringConstraints(max_length=100)]] = (
        None  # temporarily optional
    )
    user_name: Annotated[str, StringConstraints(max_length=20)]
    user_guid: Union[
        Annotated[str, StringConstraints(min_length=32, max_length=32)], None
    ]
    create_user: Annotated[str, StringConstraints(max_length=100)]
    update_user: Optional[Annotated[str, StringConstraints(max_length=100)]] = None

    model_config = ConfigDict(from_attributes=True)


class FamUserType(BaseModel):
    user_type_code: famConstants.UserType = Field(alias="code")
    description: Annotated[str, StringConstraints(max_length=35)]

    # required to set populate_by_name for alias fields
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FamUserInfo(BaseModel):
    user_name: Annotated[str, StringConstraints(max_length=20)]
    user_type_relation: FamUserType = Field(alias="user_type")
    first_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        from_attributes=True,
        fields={
            "user_guid": {"exclude": True},
            "create_user": {"exclude": True},
            "update_user": {"exclude": True},
        },
        populate_by_name=True,
    )


class FamUserUpdateResponse(BaseModel):
    total_db_users_count: int
    current_page: int
    users_count_on_page: int
    success_user_id_list: List[int]
    failed_user_id_list: List[int]
    ignored_user_id_list: List[int]
    mismatch_user_list: List[int]


# --------------------------------- FAM Forest Client--------------------------------- #
class FamForestClientCreate(BaseModel):
    # Note, the request may contain string(with leading '0')
    forest_client_number: Annotated[str, StringConstraints(max_length=8)]
    # client_name: str
    create_user: Annotated[str, StringConstraints(max_length=100)]

    model_config = ConfigDict(from_attributes=True)


# This is not an object from FAM model. It is an helper class to map Forest Client API
# client status into FAM's status needs (Active/Inactive).
class FamForestClientStatus(BaseModel):
    status_code: famConstants.FamForestClientStatusType
    description: Annotated[str, StringConstraints(max_length=10)]

    @staticmethod
    def to_fam_status(forest_client_status_code: str):
        # Map Forest Client API's 'clientStatusCode' to FAM
        accepted_api_active_codes = [famConstants.FOREST_CLIENT_STATUS["CODE_ACTIVE"]]
        status_code = (
            famConstants.FamForestClientStatusType.ACTIVE
            if forest_client_status_code in accepted_api_active_codes
            else famConstants.FamForestClientStatusType.INACTIVE
        )
        description = (
            famConstants.DESCRIPTION_ACTIVE
            if status_code == famConstants.FamForestClientStatusType.ACTIVE
            else famConstants.DESCRIPTION_INACTIVE
        )
        status = FamForestClientStatus(status_code=status_code, description=description)
        return status


class FamForestClient(BaseModel):
    client_name: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    forest_client_number: Annotated[str, StringConstraints(max_length=8)]
    status: Optional[FamForestClientStatus] = None

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_api_json(json_dict):
        LOGGER.debug(f"from_api_json - {json_dict}")
        client_name = json_dict["clientName"]
        forest_client_number = json_dict["clientNumber"]
        forest_client_status_code = json_dict[famConstants.FOREST_CLIENT_STATUS["KEY"]]
        status = FamForestClientStatus.to_fam_status(forest_client_status_code)
        fc = FamForestClient(
            client_name=client_name,
            forest_client_number=forest_client_number,
            status=status,
        )
        return fc


# --------------------------------- FAM Role--------------------------------- #
class FamRoleCreate(BaseModel):
    role_name: Annotated[str, StringConstraints(max_length=100)]
    role_purpose: Union[Annotated[str, StringConstraints(max_length=300)], None] = None
    parent_role_id: Union[int, None] = Field(
        default=None, title="Reference role_id to higher role"
    )
    application_id: int = Field(title="Application this role is associated with")
    role_type_code: famConstants.RoleType
    forest_client_number: Union[
        Annotated[str, StringConstraints(max_length=8)], None
    ] = Field(default=None, title="Forest Client this role is associated with")
    create_user: Annotated[str, StringConstraints(max_length=100)]
    client_number: Optional[FamForestClientCreate] = None

    model_config = ConfigDict(from_attributes=True)


class FamRoleMin(BaseModel):
    role_name: Annotated[str, StringConstraints(max_length=100)]
    role_type_code: famConstants.RoleType
    application: FamApplication

    model_config = ConfigDict(from_attributes=True)


class FamRoleWithClient(FamRoleMin):
    role_id: int
    client_number: Optional[FamForestClient] = None
    parent_role: Optional[FamRoleMin] = None

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        from_attributes=True,
        fields={
            "update_user": {"exclude": True},
            "role_purpose": {"exclude": True},
            "parent_role_id": {"exclude": True},
            "application_id": {"exclude": True},
            "forest_client_number": {"exclude": True},
            "role_id": {"exclude": True},
            "create_user": {"exclude": True},
        },
    )


# --------------------------------- FAM User Role Assignment--------------------------------- #
# Role assignment with one role at a time for the user.
class FamUserRoleAssignmentCreate(BaseModel):
    user_name: Annotated[
        str, StringConstraints(min_length=3, max_length=20)
    ]  # IDIM search max length
    user_guid: Annotated[str, StringConstraints(min_length=32, max_length=32)]
    user_type_code: famConstants.UserType
    role_id: int
    forest_client_numbers: Union[
        List[Annotated[str, StringConstraints(min_length=1, max_length=8)]], None
    ] = None
    requires_send_user_email: bool = False

    model_config = ConfigDict(from_attributes=True)


class FamApplicationUserRoleAssignmentGet(BaseModel):
    user_role_xref_id: int
    user_id: int
    role_id: int
    user: FamUserInfo
    role: FamRoleWithClient

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True)


class FamUserRoleAssignmentCreateResponse(BaseModel):
    status_code: int
    detail: FamApplicationUserRoleAssignmentGet
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FamUserRoleAssignmentResponse(BaseModel):
    email_sending_status: famConstants.EmailSendingStatus = famConstants.EmailSendingStatus.NOT_REQUIRED
    assignments_detail: List[FamUserRoleAssignmentCreateResponse]


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
    firstName: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    lastName: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None


class IdimProxyBceidInfo(BaseModel):
    found: bool
    userId: Annotated[str, StringConstraints(max_length=20)]
    guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    businessGuid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    businessLegalName: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    firstName: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    lastName: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None


# ------------------------------------- GC Notify Integraion ---------------------------------------- #
class GCNotifyGrantAccessEmailParam(BaseModel):
    first_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    application_name: Annotated[str, StringConstraints(max_length=35)]
    role_list_string: Annotated[str, StringConstraints(max_length=500)]
    application_team_contact_email: Optional[EmailStr] = None
    send_to_email: EmailStr


# ------------------------------------- Forest Client API Integraion ---------------------------------------- #
class ForestClientIntegrationFindResponse(BaseModel):
    clientNumber: str
    clientName: str
    clientStatusCode: str
    clientTypeCode: str


# ---------- System schema objects ---------- #
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
    user_name: Annotated[str, StringConstraints(max_length=20)]
    # "B"(BCeID) or "I"(IDIR). It is the IDP provider.
    user_type_code: Union[famConstants.UserType, None] = None
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
        return (
            self.user_type_code == famConstants.UserType.BCEID
            and self.is_delegated_admin
        )

    model_config = ConfigDict(from_attributes=True)


class TargetUser(Requester):
    """
    Inherit from the class "Requester". Same as Requester, the TargetUser can
    be transformed from FamUser db model.
    """

    user_id: Optional[int] = None
    first_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None
