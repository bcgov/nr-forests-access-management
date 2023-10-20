import logging
from datetime import datetime
from typing import List, Optional, Union

from pydantic import StringConstraints, ConfigDict, BaseModel, EmailStr, Field

from . import constants as famConstants
from typing_extensions import Annotated

LOGGER = logging.getLogger(__name__)


class FamGroupPost(BaseModel):
    group_name: Annotated[str, StringConstraints(max_length=100)]
    purpose: Annotated[str, StringConstraints(max_length=200)]
    create_user: Annotated[str, StringConstraints(max_length=60)]
    parent_group_id: int
    update_user: Optional[Annotated[str, StringConstraints(max_length=60)]] = None

    model_config = ConfigDict(from_attributes=True)


class FamGroupGet(FamGroupPost):
    group_id: int
    create_date: datetime
    update_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FamApplicationClient(BaseModel):
    application_client_id: int
    cognito_client_id: Annotated[str, StringConstraints(max_length=32)]
    create_user: Annotated[str, StringConstraints(max_length=60)]
    create_date: datetime
    update_user: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    update_date: datetime

    model_config = ConfigDict(from_attributes=True)


class FamApplicationCreate(BaseModel):
    application_name: Annotated[str, StringConstraints(max_length=100)]
    application_description: Annotated[str, StringConstraints(max_length=200)]
    application_client_id: Optional[int] = None
    app_environment: Optional[famConstants.AppEnv] = None

    model_config = ConfigDict(from_attributes=True)


class FamApplication(FamApplicationCreate):
    application_id: int
    create_user: Annotated[str, StringConstraints(max_length=60)]
    create_date: datetime
    update_user: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    update_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FamUser(BaseModel):
    user_type_code: famConstants.UserType
    cognito_user_id: Optional[Annotated[str, StringConstraints(max_length=100)]] = None  # temporarily optional
    user_name: Annotated[str, StringConstraints(max_length=100)]
    user_guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    create_user: Annotated[str, StringConstraints(max_length=60)]
    update_user: Optional[Annotated[str, StringConstraints(max_length=60)]] = None

    model_config = ConfigDict(from_attributes=True)


class FamRoleTypeGet(BaseModel):
    role_type_code: famConstants.RoleType
    description: Annotated[str, StringConstraints(max_length=100)]
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    update_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Role assignment with one role at a time for the user.
class FamUserRoleAssignmentCreate(BaseModel):
    user_name: Annotated[str, StringConstraints(min_length=3, max_length=100)] # db max length
    user_type_code: famConstants.UserType
    role_id: int
    forest_client_number: Union[
        Annotated[str, StringConstraints(min_length=1, max_length=8)], None
    ] = None

    model_config = ConfigDict(from_attributes=True)


class FamUserRoleAssignmentGet(BaseModel):
    user_role_xref_id: int
    user_id: int
    role_id: int
    application_id: int

    model_config = ConfigDict(from_attributes=True)


class FamForestClientCreate(BaseModel):
    # Note, the request may contain string(with leading '0')
    forest_client_number: Annotated[str, StringConstraints(max_length=8)]
    # client_name: str
    create_user: Annotated[str, StringConstraints(max_length=60)]

    model_config = ConfigDict(from_attributes=True)


class FamRoleCreate(BaseModel):
    role_name: Annotated[str, StringConstraints(max_length=100)]
    role_purpose: Union[Annotated[str, StringConstraints(max_length=200)], None] = None
    parent_role_id: Union[int, None] = Field(
        default=None, title="Reference role_id to higher role"
    )
    application_id: int = Field(title="Application this role is associated with")
    forest_client_number: Union[Annotated[str, StringConstraints(max_length=8)], None] = Field(
        default=None, title="Forest Client this role is associated with"
    )
    create_user: Annotated[str, StringConstraints(max_length=60)]
    role_type_code: famConstants.RoleType
    client_number: Optional[FamForestClientCreate] = None

    model_config = ConfigDict(from_attributes=True)


class FamRoleGet(FamRoleCreate):
    role_id: int
    update_user: Union[Annotated[str, StringConstraints(max_length=60)], None] = None
    create_date: Union[datetime, None] = None
    update_date: Union[datetime, None] = None

    application: Union[FamApplication, None] = None

    model_config = ConfigDict(from_attributes=True)


class FamUserGet(FamUser):
    user_id: int
    create_date: datetime
    update_date: Optional[datetime] = None

    role: Union[FamRoleCreate, None] = None

    model_config = ConfigDict(from_attributes=True)


class FamApplicationRole(FamRoleCreate):
    role_id: int

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, fields={"create_user": {"exclude": True}})


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


class FamRoleMin(BaseModel):
    role_name: Annotated[str, StringConstraints(max_length=100)]
    role_type_code: famConstants.RoleType
    application_id: int

    model_config = ConfigDict(from_attributes=True)


class FamRoleWithClient(FamRoleCreate):
    role_id: int
    client_number: Optional[FamForestClient] = None
    parent_role: Optional[FamRoleMin] = None

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, fields={
        "update_user": {"exclude": True},
        "role_purpose": {"exclude": True},
        "parent_role_id": {"exclude": True},
        "application_id": {"exclude": True},
        "forest_client_number": {"exclude": True},
        "role_id": {"exclude": True},
        "create_user": {"exclude": True},
    })


class FamUserType(BaseModel):
    user_type_code: famConstants.UserType = Field(alias="code")
    description: Annotated[str, StringConstraints(max_length=35)]

    # required to set populate_by_name for alias fields
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FamUserOnlyName(FamUser):
    user_type_relation: FamUserType = Field(alias="user_type")

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, fields={
        "user_guid": {"exclude": True},
        "create_user": {"exclude": True},
        "update_user": {"exclude": True},
    }, populate_by_name=True)


class FamApplicationUserRoleAssignmentGet(FamUserRoleAssignmentGet):
    user: FamUserOnlyName
    role: FamRoleWithClient
    application_id: Optional[Union[int, None]] = None

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, fields={
        "application_id": {"exclude": True},
        "user_id": {"exclude": True},
        "role_id": {"exclude": True},
    })


class IdimProxySearchParamIdir(BaseModel):
    userId: Annotated[str, StringConstraints(max_length=15)]  # param for Idim-Proxy search of this form (not snake case)


class IdimProxyIdirInfo(BaseModel):
    # property returned from Idim-Proxy search of this form (not snake case)
    found: bool
    userId: Optional[Annotated[str, StringConstraints(max_length=15)]] = None
    displayName: Optional[Annotated[str, StringConstraints(max_length=50)]] = None

    @staticmethod
    def from_api_json(json_dict):
        info = IdimProxyIdirInfo(
            found=json_dict["found"],
            userId=json_dict["userId"],
            displayName=json_dict["displayName"],
        )
        return info


class GCNotifyGrantAccessEmailParam(BaseModel):
    user_name: Annotated[str, StringConstraints(max_length=15)]
    application_name: Annotated[str, StringConstraints(max_length=35)]
    send_to_email: EmailStr


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
    access_roles: Union[List[Annotated[str, StringConstraints(max_length=50)]], None] = None

    model_config = ConfigDict(from_attributes=True)

class TargetUser(Requester):
    pass