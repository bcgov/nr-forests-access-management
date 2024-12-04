from typing import List

from api.app.constants import (DEFAULT_FC_API_SEARCH_PAGE,
                               DEFAULT_FC_API_SEARCH_PAGE_SIZE)
from pydantic import BaseModel


class ForestClientIntegrationFindResponseSchema(BaseModel):
    clientNumber: str
    clientName: str
    clientStatusCode: str
    clientTypeCode: str


class ForestClientIntegrationSearchParmsSchema(BaseModel):
    forest_client_numbers: List[str]
    page: int = DEFAULT_FC_API_SEARCH_PAGE
    size: int = DEFAULT_FC_API_SEARCH_PAGE_SIZE