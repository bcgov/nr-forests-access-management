from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

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

# class FamRole(BaseModel):

#     role_id: int
#     role_name: str
    # role_purpose = Column(String(200), nullable=False)
    # parent_role_id = Column(Integer, ForeignKey("fam_role.role_id"))
    # application_id = Column(
    #     Integer, ForeignKey("fam_application.application_id"), nullable=False
    # )
    # client_number_id = Column(Integer, ForeignKey("fam_forest_client.client_number_id"))
    # create_user = Column(String(30), nullable=False)
    # create_date = Column(
    #     TIMESTAMP(precision=6), nullable=False, server_default=text("CURRENT_DATE")
    # )
    # update_user = Column(String(30), nullable=False)
    # update_date = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_DATE"))

    # application = relationship("FamApplication")
    # client_number = relationship("FamForestClient")
    # parent_role = relationship("FamRole", remote_side=[role_id])
    # users = relationship("FamUser", secondary="fam_user_role_xref")


