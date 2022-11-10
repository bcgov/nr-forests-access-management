from datetime import datetime
from typing import Optional, Union, List

from pydantic import BaseModel, Field

from . import constants as famConstants


class FamGroupPost(BaseModel):
    group_name: str
    purpose: str
    create_user: str
    parent_group_id: int
    update_user: str

    class Config:
        orm_mode = True


class FamGroupGet(FamGroupPost):
    group_id: int
    create_date: datetime
    update_date: datetime

    class Config:
        orm_mode = True


class FamApplicationClient(BaseModel):
    application_client_id: int
    cognito_client_id: str
    create_user: str
    create_date: datetime
    update_user: str
    update_date: datetime

    class Config:
        orm_mode = True


class FamApplicationCreate(BaseModel):
    application_name: str
    application_description: str
    application_client_id: Optional[int]

    class Config:
        orm_mode = True


class FamApplication(FamApplicationCreate):
    application_id: int
    create_user: str
    create_date: datetime
    update_user: str
    update_date: datetime

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


class FamRoleCreate(BaseModel):
    role_name: str
    role_purpose: str
    parent_role_id: Union[int, None] = Field(
        default=None, title="Reference role_id to higher role"
    )
    application_id: Union[int, None] = Field(
        default=None, title="Application this role is associated with"
    )
    forest_client_number: Union[str, None] = Field(
        default=None, title="Forest Client this role is associated with"
    )
    create_user: str
    role_type_code: str

    class Config:
        orm_mode = True


class FamApplicationRoleGet(FamApplication):
    fam_role: List[FamRoleCreate]

    class Config:
        orm_mode = True


class FamUserGet(FamUser):
    user_id: int
    create_date: datetime
    update_date: Optional[datetime]

    role: Union[FamRoleCreate, None]

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


class FamRoleGet(FamRoleCreate):
    role_id: int
    update_user: Union[str, None]
    create_date: Union[datetime, None]
    update_date: Union[datetime, None]

    application: Union[FamApplication, None]

    class Config:
        """allows serialization of orm data struct"""

        orm_mode = True


# Role assignment with one role at a time for the user.
class FamUserRoleAssignmentCreate(BaseModel):
    user_name: str
    user_type_code: famConstants.UserType
    role_id: int
    forest_client_number: Union[str, None]

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
    client_name: str
    create_user: str

    class Config:
        orm_mode = True


class FamForestClientGet(FamForestClientCreate):
    update_user: Union[str, None]
    create_date: Union[datetime, None]
    update_date: Union[datetime, None]

    class Config:
        orm_mode = True
