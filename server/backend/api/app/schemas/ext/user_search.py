

from typing import List, Optional, Self

from api.app.constants import (EXT_APPLICATION_NAME_MAX_LEN,
                               EXT_DEFAULT_PAGE_SIZE, EXT_IDIM_SEARCH_MAX_PAGE_SIZE,
                               EXT_MAX_FIRST_NAME_LEN,
                               EXT_MAX_IDP_USERNAME_LEN, EXT_MAX_LAST_NAME_LEN,
                               EXT_MIN_PAGE_SIZE,
                               EXT_MAX_ROLE_LEN, EXT_MAX_ROLE_LIST_LEN,
                               EXT_ROLE_DISPLAY_NAME_MAX_LEN,
                               FIRST_NAME_MAX_LEN, LAST_NAME_MAX_LEN,
                               USER_NAME_MAX_LEN, IDPType, ScopeType)
from fastapi import Query
from pydantic import (BaseModel, ConfigDict, Field, StringConstraints,
                      field_validator, model_validator)
from typing_extensions import Annotated


class ExtApplicationUserSearchSchema(BaseModel):
    """
    External API request schema.
    For user search.
    """
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
        Query(
            default=None,
            max_length=EXT_MAX_ROLE_LIST_LEN,
            description=f"List of user roles (code, e.g., 'ILCR_SUBMITTER') to filter by (each max {EXT_MAX_ROLE_LEN} chars)"),
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


class ExtIdirUserSearchParamSchema(BaseModel):
    """
    External API request schema for IDIR users search.
    """
    first_name: Optional[str] = Field(
        Query(
            default=None,
            max_length=EXT_MAX_FIRST_NAME_LEN,
            description="IDIR first name search value (min 2 chars)",
        ),
        alias="firstName",
    )
    last_name: Optional[str] = Field(
        Query(
            default=None,
            max_length=EXT_MAX_LAST_NAME_LEN,
            description="IDIR last name search value (min 2 chars)",
        ),
        alias="lastName",
    )
    user_id: Optional[str] = Field(
        Query(
            default=None,
            max_length=EXT_MAX_IDP_USERNAME_LEN,
            description="IDIR user id search value (min 2 chars)",
        ),
        alias="userId",
    )

    # Note, IDIM Webservice does not provide page number for filtering. If the values in the search parameters are too broad,
    # the API will only return the page_size number of records from the top of the search result.
    page_size: int = Field(
        Query(
            default=EXT_DEFAULT_PAGE_SIZE,
            ge=EXT_MIN_PAGE_SIZE,
            le=EXT_IDIM_SEARCH_MAX_PAGE_SIZE,
            description="Number of records to return",
        ),
        alias="pageSize",
    )

    @field_validator("first_name", "last_name", "user_id", mode="before")
    @classmethod
    def normalize_search_text(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            normalized_value = value.strip()
            return normalized_value or None
        return value

    @model_validator(mode="after")
    def validate_search_inputs(self) -> Self:
        fields = [
            ("firstName", self.first_name),
            ("lastName", self.last_name),
            ("userId", self.user_id),
        ]

        if all(field_value is None for _, field_value in fields):
            raise ValueError(
                "At least one of firstName, lastName, or userId must be provided"
            )

        for field_name, field_value in fields:
            if field_value is not None and len(field_value) < 2:
                raise ValueError(
                    f"{field_name} must be at least 2 characters when provided"
                )

        return self

    model_config = ConfigDict(from_attributes=True)


class ExtRoleWithScopeSchema(BaseModel):
    """
    External API response schema.
    For returning user search results: role detail info.
    """
    application_name: Optional[Annotated[str, StringConstraints(
        max_length=EXT_APPLICATION_NAME_MAX_LEN)]] = Field(default=None, alias="applicationName")
    role_name: Optional[Annotated[str, StringConstraints(
        max_length=EXT_MAX_ROLE_LEN)]] = Field(default=None, alias="roleName")
    role_display_name: Optional[Annotated[str, StringConstraints(
        max_length=EXT_ROLE_DISPLAY_NAME_MAX_LEN)]] = Field(default=None, alias="roleDisplayName")
    scope_type: Optional[ScopeType] = Field(default=None, alias="scopeType")
    value: List[str] = Field(default=[], alias="value")

    model_config = ConfigDict(from_attributes=True)


class ExtApplicationUserSearchGetSchema(BaseModel):
    """
    External API response schema.
    For returning user search results: user detail and roles info.
    """
    first_name: Optional[Annotated[str, StringConstraints(
        max_length=FIRST_NAME_MAX_LEN)]] = Field(default=None, alias="firstName")
    last_name: Optional[Annotated[str, StringConstraints(
        max_length=LAST_NAME_MAX_LEN)]] = Field(default=None, alias="lastName")
    idp_username: Optional[Annotated[str, StringConstraints(
        max_length=USER_NAME_MAX_LEN)]] = Field(default=None, alias="idpUsername")
    idp_user_guid: Optional[str] = Field(default=None, alias="idpUserGuid")
    idP_type: Optional[IDPType] = Field(default=None, alias="idpType")

    roles: List[ExtRoleWithScopeSchema] = Field(default=[], alias="roles")

    model_config = ConfigDict(from_attributes=True)
