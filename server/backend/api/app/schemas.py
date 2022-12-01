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

# TODO: check that this is still needed
class FamApplicationRole(FamRoleCreate):
    role_id: int

    class Config:
        orm_mode = True
        fields = {'create_user': {'exclude': True}}


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


# class FamUserRoleXref(FamUserRoleAssignmentGet):
#     #oveerriding FamUserRoleAssignmentGet to make application optional
#     user: FamUser
#     role: FamRoleCreate
#     application_id: Optional[Union[str, None]]

#     class Config:
#         orm_mode = True
#         #fields = {'create_user': {'exclude': True}}

# appUserRoleAssignments.fam_role[0].fam_user_role_xref
#class FamRole_FamUserRoleXref(FamRoleCreate):
    #fam_user_role_xref: List[FamUserRoleXref]


    #class Config:
    #        orm_mode = True

# [<api.app.models.model.FamRole object at 0x7f71842c26d0>]
# FamApplicationUserRoleAssignmentGet
# response -> fam_role -> 0 -> fam_user_role_xref -> 0 -> application_id
#  field required (type=value_error.missing)
# TODO: probably delete this class


class FamForestClient(BaseModel):
    client_name: str
    forest_client_number: int

    class Config:
        orm_mode = True


class FamRoleWithClient(FamRoleCreate):
    role_id: int
    client_number: Optional[FamForestClient]

    class Config:
        orm_mode = True
        fields = {'update_user': {'exclude': True},
                  'role_purpose': {'exclude': True},
                  'parent_role_id': {'exclude': True},
                  'application_id': {'exclude': True},
                  'forest_client_number': {'exclude': True},
                  'role_id': {'exclude': True},
                  'create_user': {'exclude': True},
                  }

class FamUserOnlyName(FamUser):
    class Config:
        orm_mode = True
        fields = {'user_guid': {'exclude': True},
                  'create_user': {'exclude': True},
                  'update_user': {'exclude': True}
                  }


class FamApplicationUserRoleAssignmentGet(FamUserRoleAssignmentGet):
    user: FamUserOnlyName
    role: FamRoleWithClient
    application_id: Optional[Union[int, None]]

    class Config:
        orm_mode = True
        fields = {'application_id': {'exclude': True},
                  'user_id': {'exclude': True},
                  'role_id': {'exclude': True}
                  }



"""
LIST
    user_role_xref_id: role assignment id


    user_name
    user_type (idir/bceid)
    role_name
    forest_client_number




attributes:
    application_id - thinking to verify that its working for now
    fam_user_role_xref:
        LIST
            user_role_xref_id - assignment id
            user:
                user_id
                user_name
            role:
                role_name
                role_type_code
                role_id


    forest_client_id

----- From Basil ----
 assignment_id: 1,
user_id: 'foo-test',
user_domain: 'IDIR',
role: 'Reviewer',
},
{
assignment_id: 2,
user_id: 'bar-test',
user_domain: 'BCeID',
role: 'Submitter',
forest_client_number: '01234567'
"""