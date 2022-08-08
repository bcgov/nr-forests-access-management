from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class FamApplicationClient(BaseModel):
    application_client_id: int
    cognito_client_id: str
    create_user: str
    create_date: datetime
    update_user: str
    update_date: datetime

    class Config:
        orm_mode = True


class FamApplication(BaseModel):
    application_id: int
    application_name: str
    applicationdescription: str
    application_client_id: int
    create_user: str
    create_date: datetime
    update_user: str
    update_date: datetime

    class Config:
        orm_mode = True


class FamApplicationCreate(BaseModel):
    application_name: str
    applicationdescription: str
    application_client_id: int
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


class FamUserGet(FamUser):
    user_id: int
    create_date: datetime
    update_date: datetime

    class Config:
        """allows serialization of orm data struct"""

        orm_mode = True


class FamRole(BaseModel):
    role_id: int
    role_name: str
    role_purpose: str
    parent_role_id: int
    # application_id = Column(
    #     Integer, ForeignKey("fam_application.application_id"), nullable=False
    # )
    client_number_id: int
    create_user: str
    # create_date = Column(
    #     TIMESTAMP(precision=6), nullable=False, server_default=text("CURRENT_DATE")
    # )
    update_user: str
    # update_date: datetime.datetime
    # application = relationship("FamApplication")
    # client_number = relationship("FamForestClient")
    # parent_role = relationship("FamRole", remote_side=[role_id])
    # users = relationship("FamUser", secondary="fam_user_role_xref")


class FamRoleGet(FamRole):
    role_id: int
    create_date: datetime
    update_date: datetime

    class Config:
        """allows serialization of orm data struct"""

        orm_mode = True
