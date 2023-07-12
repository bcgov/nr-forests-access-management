import logging
from typing import List

from api.app.integration.idim_proxy import IdimProxyService
from fastapi import APIRouter, Query, Request

LOGGER = logging.getLogger(__name__)

router = APIRouter()

@router.get("/idir", response_model=List[dict])
def idir_search(
    request: Request,
    user_id: str = Query(min_length=3)
):
    LOGGER.debug(f"Searching IDIR user with parameter user_id: {request.query_params}")
    idim_proxy_api = IdimProxyService(request)
    search_result = idim_proxy_api.search_idir()
    return search_result