

from typing import List, Optional

from api.app.constants import (EXT_MAX_FIRST_NAME_LEN,
                               EXT_MAX_IDP_USERNAME_LEN, EXT_MAX_LAST_NAME_LEN,
                               EXT_MAX_ROLE_LEN, IDPType)
from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApplicationUserSearchSchema(BaseModel):
    idp_type: Optional[IDPType] = Field(
        Query(default=None, description="Identity provider type. Available values: IDIR, BCEID, BCSC"),
        alias="idpType"
    )
    idp_username: Optional[str] = Field(
        Query(
            default=None,
            max_length=EXT_MAX_IDP_USERNAME_LEN,
            description="Username from the identity provider"
        ),
        alias="idpUsername"
    )
    first_name: Optional[str] = Field(
        Query(
            default=None,
            max_length=EXT_MAX_FIRST_NAME_LEN,
            description="User's first name"
        ),
        alias="firstName"
    )
    last_name: Optional[str] = Field(
        Query(
            default=None,
            max_length=EXT_MAX_LAST_NAME_LEN,
            description="User's last name"
        ),
        alias="lastName"
    )
    role: Optional[List[str]] = Field(
        Query(default=None, description=f"List of user roles to filter by (each max {EXT_MAX_ROLE_LEN} chars)"),
        alias="role"
    )

    # helper function to validate each role length, using field_validator.
    @classmethod
    def validate_role_length(cls, v):
        if v is not None:
            for item in v:
                if item is not None and len(item) > EXT_MAX_ROLE_LEN:
                    raise ValueError(f"Each role must be at most {EXT_MAX_ROLE_LEN} characters long. Got: '{item}' ({len(item)} chars)")
        return v

    @field_validator('role', mode='before')
    def check_role_list(cls, v):
        return cls.validate_role_length(v)

    model_config = ConfigDict(from_attributes=True)
