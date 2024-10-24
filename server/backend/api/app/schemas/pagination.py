
from abc import ABC
from typing import Generic, List

from api.app.constants import (DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MIN_PAGE,
                               MIN_PAGE_SIZE, SEARCH_FIELD_MAX_LENGTH,
                               SEARCH_FIELD_MIN_LENGTH, SortOrderEnum, T,
                               UserRoleSortByEnum)
from fastapi import Query
from pydantic import BaseModel, Field

"""
Schema objects for the backend pagination, sorting, filtering related purpose.
"""

"""
Note: FastAPI does not seem to work well with Pydantic for Query Parameter + Swagger.
To use Pydantic class in "router's endpoint" as FastAPI query parameter, it needs to wrap the property with "Field(Query(...))"
like below example in order to get validation correct and with 'description' shows up at Swagger:
    page_number: int | None = Field(Query(default=1, ge=1, description="page number to get the paged data"))

More over, the endpoint also need to use "Depends()" for function argument, like below exampe:
    def get_fam_application_user_role_assignment(
        application_id: int,
        page_params: PageParamsSchema = Depends(),
        ...
    )

And, in this case, the validation error default from Pydantic will not be 400, it will be 422 (from Pydantic)

Ref: https://stackoverflow.com/questions/75998227/how-to-define-query-parameters-using-pydantic-model-in-fastapi
"""

class PageParamsSchema(BaseModel, ABC):
    """
    Abstract class for request query params for backend API pagination, sorting and filtering.
    This is the base schema for common fields. Endpoints need to extend this class for specific needs.
    """
    page: int | None = Field(Query(
        default=MIN_PAGE, ge=MIN_PAGE, description="Page number", alias="pageNumber"
    ))
    size: int | None = Field(Query(
        default=DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE, description="Number of records per page", alias="pageSize"
    ))

    search: str | None = Field(Query(
        default=None, min_length=SEARCH_FIELD_MIN_LENGTH, max_length=SEARCH_FIELD_MAX_LENGTH, description="Search by keyword"
    ))

    sort_order: SortOrderEnum | None = Field(Query(default=SortOrderEnum.ASC, description="Column sorting order by", alias="sortOrder"))


class UserRolePageParamsSchema(PageParamsSchema):
    sort_by: UserRoleSortByEnum | None = Field(Query(default=UserRoleSortByEnum.USER_NAME, description="Column to be sorted by", alias="sortBy"))


class PageResultMetaSchema(BaseModel):
    total: int = Field(description='Total records counts for query conditions')
    number_of_pages: int = Field(description='Total pages for query records')
    page_number: int = Field(description='Page number')
    page_size: int = Field(description='Number of records per page')


class PagedResultsSchema(BaseModel, Generic[T]):
    """
    API pagination return schema.
    Use Python generice type for return type.
    """
    meta: PageResultMetaSchema
    results: List[T] = Field(description='Paged results')