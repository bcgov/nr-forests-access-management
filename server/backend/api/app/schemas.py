from datetime import datetime
import logging
from typing import Optional, Union

from pydantic import BaseModel, Field, constr

from . import constants as famConstants

LOGGER = logging.getLogger(__name__)


class FamGroupPost(BaseModel):
    group_name: str
    purpose: str
    create_user: str
    parent_group_id: int
    update_user: Optional[str]

    class Config:
        orm_mode = True


class FamGroupGet(FamGroupPost):
    group_id: int
    create_date: datetime
    update_date: Optional[datetime]

    class Config:
        orm_mode = True


class FamApplicationClient(BaseModel):
    application_client_id: int
    cognito_client_id: str
    create_user: str
    create_date: datetime
    update_user: Optional[str]
    update_date: datetime

    class Config:
        orm_mode = True


class FamApplicationCreate(BaseModel):
    application_name: str
    application_description: str
    application_client_id: Optional[int]
    app_environment: Optional[famConstants.AppEnv]

    class Config:
        orm_mode = True


class FamApplication(FamApplicationCreate):
    application_id: int
    create_user: str
    create_date: datetime
    update_user: Optional[str]
    update_date: Optional[datetime]

    class Config:
        orm_mode = True


class FamUser(BaseModel):
    user_type_code: famConstants.UserType
    cognito_user_id: Optional[str]  # temporarily optional
    user_name: str
    user_guid: Optional[str]
    create_user: str
    update_user: Optional[str]

    class Config:
        orm_mode = True


class FamRoleTypeGet(BaseModel):
    role_type_code: str
    description: str
    effective_date: datetime
    expiry_date: Optional[datetime]
    update_date: Optional[datetime]

    class Config:
        """allows serialization of orm data struct"""

        orm_mode = True


# Role assignment with one role at a time for the user.
class FamUserRoleAssignmentCreate(BaseModel):
    user_name: str
    user_type_code: famConstants.UserType
    role_id: int
    forest_client_number: Union[constr(min_length=1, max_length=8), None]

    class Config:
        orm_mode = True


class FamUserRoleAssignmentGet(BaseModel):
    user_role_xref_id: int
    user_id: int
    role_id: int
    application_id: int

    class Config:
        orm_mode = True


class FamForestClientCreate(BaseModel):
    # Note, the request may contain string(with leading '0')
    forest_client_number: str
    #client_name: str
    create_user: str

    class Config:
        orm_mode = True


class FamRoleCreate(BaseModel):
    role_name: str
    role_purpose: Union[str, None]
    parent_role_id: Union[int, None] = Field(
        default=None, title="Reference role_id to higher role"
    )
    application_id: int = Field(
        title="Application this role is associated with"
    )
    forest_client_number: Union[str, None] = Field(
        default=None, title="Forest Client this role is associated with"
    )
    create_user: str
    role_type_code: str
    client_number: Optional[FamForestClientCreate]

    class Config:
        """allows serialization of orm data struct"""

        orm_mode = True


class FamRoleGet(FamRoleCreate):
    role_id: int
    update_user: Union[str, None]
    create_date: Union[datetime, None]
    update_date: Union[datetime, None]

    application: Union[FamApplication, None]

    class Config:
        """allows serialization of orm data struct"""

        orm_mode = True


class FamUserGet(FamUser):
    user_id: int
    create_date: datetime
    update_date: Optional[datetime]

    role: Union[FamRoleCreate, None]

    class Config:
        orm_mode = True


class FamApplicationRole(FamRoleCreate):
    role_id: int

    class Config:
        orm_mode = True
        fields = {"create_user": {"exclude": True}}


# This is not an object from FAM model. It is an helper class to map Forest Client API
# client status into FAM's status needs (Active/Inactive).
class FamForestClientStatus(BaseModel):
    status_code: famConstants.FamForestClientStatusType
    description: str

    @staticmethod
    def to_fam_status(forest_client_status_code: str):
        # Map Forest Client API's 'clientStatusCode' to FAM
        accepted_api_active_codes = [famConstants.FOREST_CLIENT_STATUS["CODE_ACTIVE"]]
        DESCRIPTION_ACTIVE = "Active"
        DESCRIPTION_INACTIVE = "Inactive"
        status_code = (
            famConstants.FamForestClientStatusType.ACTIVE
            if forest_client_status_code in accepted_api_active_codes
            else famConstants.FamForestClientStatusType.INACTIVE
        )
        description = (
            DESCRIPTION_ACTIVE
            if status_code == famConstants.FamForestClientStatusType.ACTIVE
            else DESCRIPTION_INACTIVE
        )
        status = FamForestClientStatus(
            status_code=status_code,
            description=description
        )
        return status


class FamForestClient(BaseModel):
    client_name: Optional[str]
    forest_client_number: str
    status: Optional[FamForestClientStatus]

    class Config:
        orm_mode = True

    @staticmethod
    def from_api_json(json_dict):
        LOGGER.debug(f"from_api_json - {json_dict}")
        client_name = json_dict['clientName']
        forest_client_number = json_dict['clientNumber']
        forest_client_status_code = json_dict[famConstants.FOREST_CLIENT_STATUS["KEY"]]
        status = FamForestClientStatus.to_fam_status(forest_client_status_code)
        fc = FamForestClient(
            client_name=client_name,
            forest_client_number=forest_client_number,
            status=status
        )
        return fc


class FamRoleMin(BaseModel):
    role_name: str
    role_type_code: str
    application_id: int

    class Config:
        orm_mode = True


class FamRoleWithClient(FamRoleCreate):
    role_id: int
    client_number: Optional[FamForestClient]
    parent_role: Optional[FamRoleMin]

    class Config:
        orm_mode = True
        fields = {
            "update_user": {"exclude": True},
            "role_purpose": {"exclude": True},
            "parent_role_id": {"exclude": True},
            "application_id": {"exclude": True},
            "forest_client_number": {"exclude": True},
            "role_id": {"exclude": True},
            "create_user": {"exclude": True},
        }


class FamUserType(BaseModel):
    user_type_code: famConstants.UserType = Field(alias="code")
    description: str

    class Config:
        orm_mode = True
        # required to be able to alias fields
        allow_population_by_field_name = True


class FamUserOnlyName(FamUser):
    user_type_relation: FamUserType = Field(alias="user_type")

    class Config:
        orm_mode = True
        fields = {
            "user_guid": {"exclude": True},
            "create_user": {"exclude": True},
            "update_user": {"exclude": True},
        }
        # need this paramter to be able to alias a relationship field/property
        allow_population_by_field_name = True


class FamApplicationUserRoleAssignmentGet(FamUserRoleAssignmentGet):
    user: FamUserOnlyName
    role: FamRoleWithClient
    application_id: Optional[Union[int, None]]

    class Config:
        orm_mode = True
        fields = {
            "application_id": {"exclude": True},
            "user_id": {"exclude": True},
            "role_id": {"exclude": True},
        }
