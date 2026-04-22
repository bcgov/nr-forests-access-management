from enum import Enum
from typing import List, Optional, Self

from pydantic import (BaseModel, Field, StringConstraints, field_validator,
                      model_validator)
from typing_extensions import Annotated

from api.app.constants import (EMAIL_MAX_LEN, EXT_DEFAULT_PAGE_SIZE, EXT_IDIM_SEARCH_MAX_PAGE_SIZE,
                               EXT_MAX_FIRST_NAME_LEN, EXT_MAX_LAST_NAME_LEN,
                               EXT_MAX_IDP_USERNAME_LEN, EXT_MIN_PAGE_SIZE, FIRST_NAME_MAX_LEN,
                               LAST_NAME_MAX_LEN, USER_NAME_MAX_LEN)

class IdimSearchMatchMode(str, Enum):
    """
    IDIM webservice supports three match modes for searching IDIR users: Exact, StartsWith, and Contains.
    For simplicity, FAM will use the Contains match mode internally for all search parameters in the search endpoint.
    FAM does not expose these mode for consume.
    """
    CONTAINS = "Contains"


class IdimProxyIdirUsersSearchParamReqSchema(BaseModel):
    # Query parameters for IDIM proxy IDIR users search endpoint.
    firstName: Optional[
        Annotated[str, StringConstraints(max_length=EXT_MAX_FIRST_NAME_LEN)]
    ] = Field(default=None, description="IDIR first name search value (min 2 chars)")
    lastName: Optional[
        Annotated[str, StringConstraints(max_length=EXT_MAX_LAST_NAME_LEN)]
    ] = Field(default=None, description="IDIR last name search value (min 2 chars)")
    userId: Optional[
        Annotated[str, StringConstraints(max_length=EXT_MAX_IDP_USERNAME_LEN)]
    ] = Field(default=None, description="IDIR user id search value (min 2 chars)")

    # Note, IDIM Webservice does not provide page number for filtering. If the values in the search parameters are too broad,
    # the API will only return the page_size number of records from the top of the search result.
    pageSize: int = Field(
        default=EXT_DEFAULT_PAGE_SIZE,
        ge=EXT_MIN_PAGE_SIZE,
        le=EXT_IDIM_SEARCH_MAX_PAGE_SIZE,
        description="Number of records to return",
    )

    @field_validator("firstName", "lastName", "userId", mode="before")
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
        if self.firstName is None and self.lastName is None and self.userId is None:
            raise ValueError(
                "At least one of firstName, lastName, or userId must be provided"
            )

        fields = [
            ("firstName", self.firstName),
            ("lastName", self.lastName),
            ("userId", self.userId),
        ]

        for field_name, field_value in fields:
            if field_value is not None and len(field_value) < 2:
                raise ValueError(
                    f"{field_name} must be at least 2 characters when provided"
                )

        return self

    def to_query_params(self) -> dict[str, int | str]:
        """Build IDIM query params with the fixed `Contains` match mode."""
        query_params = self.model_dump(exclude_none=True)

        if self.firstName is not None:
            query_params["firstNameMatchMode"] = IdimSearchMatchMode.CONTAINS.value
        if self.lastName is not None:
            query_params["lastNameMatchMode"] = IdimSearchMatchMode.CONTAINS.value
        if self.userId is not None:
            query_params["userIdMatchMode"] = IdimSearchMatchMode.CONTAINS.value

        return query_params


class IdimProxyIdirUserSearchItemResSchema(BaseModel):
    # Item returned from IDIM proxy IDIR users search endpoint.
    userId: Annotated[str, StringConstraints(max_length=USER_NAME_MAX_LEN)]
    guid: Annotated[str, StringConstraints(max_length=32)]
    firstName: Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    lastName: Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    email: Annotated[str, StringConstraints(max_length=EMAIL_MAX_LEN)]


class IdimProxyIdirUsersSearchResSchema(BaseModel):
    # Response returned from IDIM proxy IDIR users search endpoint.
    totalItems: int
    pageSize: int
    items: List[IdimProxyIdirUserSearchItemResSchema]
