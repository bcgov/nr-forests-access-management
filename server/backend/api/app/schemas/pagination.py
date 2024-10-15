
from typing import Generic, List, Optional

from api.app.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MIN_PAGE, T
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from typing_extensions import Annotated


class PageParamsSchema(BaseModel):
    """ Request query params for backend API pagination """
    page_number: Optional[Annotated[int, Field(default=MIN_PAGE, ge=MIN_PAGE)]] = None
    page_size: Optional[Annotated[int, Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)]] = None


class PagedResultsSchema(GenericModel, Generic[T]):
    """ API pagination return schema """
    total: int  # total counts
    page_number: int
    results: List[T]  # current paged results