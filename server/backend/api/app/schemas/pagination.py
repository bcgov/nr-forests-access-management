
from typing import Generic, List, Optional

from api.app.constants import (DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MIN_PAGE,
                               MIN_PAGE_SIZE, T)
from fastapi import Query
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

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

And, in this working case, the validation will not be 400, it will be 422 (from Pydantic)

Ref: https://stackoverflow.com/questions/75998227/how-to-define-query-parameters-using-pydantic-model-in-fastapi
"""

class PageParamsSchema(BaseModel):
    """ Request query params for backend API pagination """
    # page_number: Annotated[int, Field(default=MIN_PAGE, ge=MIN_PAGE, description="number to get the paged data")]  # not working
    # page_number: Annotated[int, Query(default=MIN_PAGE, ge=MIN_PAGE, description="number provided to get the paged data")]  # not working
    # page_number: int = Field(default=MIN_PAGE, ge=MIN_PAGE, description="number provided to get the paged data") # not working
    # page_number: Annotated[int, Field(Query(default=MIN_PAGE, ge=MIN_PAGE, description="number to get the paged data"))] # not working
    # page_number: int | None = Field(default=1, ge=1, description="number to get the paged data")  # not working

    # The best combination of FastAPI + Pydantic for Swagger
    page_number: int | None = Field(Query(
        default=MIN_PAGE, ge=MIN_PAGE, description="page number to get the paged data"
    ))
    page_size: int | None = Field(Query(
        default=DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE, description="number of records for each page"
    ))


class PagedResultsSchema(GenericModel, Generic[T]):
    """
    API pagination return schema.
    Use Python generice type for return type.
    """
    total: int  # total counts
    page_number: int
    results: List[T]  # current paged results