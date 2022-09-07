from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field, validator


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
    user_type: str
    cognito_user_id: Optional[str]  # temporarily optional
    user_name: str
    user_guid: str
    # create_user: EmailStr
    create_user: str
    update_user: str

    @validator("user_type")
    def user_type_length(cls, v):
        if len(v) > 1:
            raise ValueError(f"value for user_type provided was {v}, " +
                             "user_type length cannot exceed 1 character")
        return v.title()

    class Config:
        orm_mode = True


class FamRole(BaseModel):
    role_name: str
    role_purpose: str
    parent_role_id: Union[int, None] = Field(default=None, title="Reference role_id to higher role")
    application_id: Union[int, None] = Field(default=None, title="Application this role is associated with")
    client_number_id: Union[int, None] = Field(default=None, title="Forest Client this role is associated with")
    create_user: str

    class Config:
        orm_mode = True


class FamUserGet(FamUser):
    user_id: int
    create_date: datetime
    update_date: Optional[datetime]

    role: Union[FamRole, None]

    class Config:
        orm_mode = True


class FamRoleGet(FamRole):
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
    user_type: str
    role_id: int
    client_number_id: Union[int, None]  # Forest Client ID

    class Config:
        orm_mode = True


class FamUserRoleAssignmentGet(BaseModel):
    user_role_xref_id: int
    user_id: int
    role_id: int

    class Config:
        orm_mode = True
