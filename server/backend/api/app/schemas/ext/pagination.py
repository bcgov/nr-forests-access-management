
from abc import ABC
from typing import Generic, List

from api.app.constants import (EXT_DEFAULT_PAGE_SIZE, EXT_MAX_PAGE_SIZE,
                               EXT_MIN_PAGE, EXT_MIN_PAGE_SIZE, T)
from fastapi import Query
from pydantic import BaseModel, Field

"""
Schema objects for external api pagination.

Ref: https://stackoverflow.com/questions/75998227/how-to-define-query-parameters-using-pydantic-model-in-fastapi
"""

class ExtPageParamsSchema(BaseModel, ABC):
    """
    Abstract class for request query params for external API pagination.
    This is the base schema for common fields. Endpoints need to extend this class.
    """
    page: int | None = Field(Query(
        default=EXT_MIN_PAGE, ge=EXT_MIN_PAGE, description="Page number - 1 index"
    ))
    size: int | None = Field(Query(
        default=EXT_DEFAULT_PAGE_SIZE, ge=EXT_MIN_PAGE_SIZE, le=EXT_MAX_PAGE_SIZE, description="Number of records per page"
    ))


class ExtUserSearchParamSchema(ExtPageParamsSchema):
    pass


class ExtPageResultMetaSchema(BaseModel):
    """
    Response metadata for external API pagination.
    """
    total: int = Field(description='Total records counts for query conditions', default=0)
    page_count: int = Field(description='Total pages for query records', alias="pageCount")
    page: int = Field(description='Current page number', ge=EXT_MIN_PAGE)
    size: int = Field(description='Number of records per page', le=EXT_MAX_PAGE_SIZE, ge=EXT_MIN_PAGE_SIZE)


class ExtUserSearchPagedResultsSchema(BaseModel, Generic[T]):
    """
    External user search API return schema.
    """
    meta: ExtPageResultMetaSchema
    users: List[T] = Field(description='Paged results')