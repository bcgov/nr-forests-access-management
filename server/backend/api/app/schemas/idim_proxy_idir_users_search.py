from enum import Enum
from typing import List, Optional, Self

from pydantic import BaseModel, Field, StringConstraints, model_validator
from typing_extensions import Annotated

from api.app.constants import (EMAIL_MAX_LEN, EXT_DEFAULT_PAGE_SIZE,
                               EXT_MAX_FIRST_NAME_LEN, EXT_MAX_LAST_NAME_LEN,
                               EXT_MAX_PAGE_SIZE, EXT_MAX_IDP_USERNAME_LEN,
                               EXT_MIN_PAGE_SIZE, FIRST_NAME_MAX_LEN,
                               LAST_NAME_MAX_LEN, USER_NAME_MAX_LEN)


class IdimSearchMatchMode(str, Enum):
    EXACT = "Exact"
    CONTAINS = "Contains"
    STARTS_WITH = "StartsWith"


class IdimProxyIdirUsersSearchParamReqSchema(BaseModel):
    # Query parameters for IDIM proxy IDIR users search endpoint.
    firstName: Optional[
        Annotated[str, StringConstraints(max_length=EXT_MAX_FIRST_NAME_LEN)]
    ] = None
    lastName: Optional[
        Annotated[str, StringConstraints(max_length=EXT_MAX_LAST_NAME_LEN)]
    ] = None
    userId: Optional[
        Annotated[str, StringConstraints(max_length=EXT_MAX_IDP_USERNAME_LEN)]
    ] = None

    firstNameMatchMode: Optional[IdimSearchMatchMode] = None
    lastNameMatchMode: Optional[IdimSearchMatchMode] = None
    userIdMatchMode: Optional[IdimSearchMatchMode] = None

    pageSize: int = Field(
        default=EXT_DEFAULT_PAGE_SIZE,
        ge=EXT_MIN_PAGE_SIZE,
        le=EXT_MAX_PAGE_SIZE,
    )

    @model_validator(mode="after")
    def validate_search_inputs(self) -> Self:
        if self.firstName is None and self.lastName is None and self.userId is None:
            raise ValueError(
                "At least one of firstName, lastName, or userId must be provided"
            )

        return self


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
