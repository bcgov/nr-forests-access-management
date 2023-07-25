import logging
from typing import Annotated, List

from api.app.integration.idim_proxy import IdimProxyService
from api.app.requester import (Requester, get_current_requester,
                               internal_only_action)
from fastapi import APIRouter, Query
from fastapi.params import Depends

ERROR_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"

LOGGER = logging.getLogger(__name__)

router = APIRouter()

@router.get("/idir", response_model=List[dict], dependencies = [Depends(internal_only_action)],)
def idir_search(
    requester: Annotated[Requester, Depends(get_current_requester)],
    user_id: str = Query(min_length=3)
):
    LOGGER.debug(f"Searching IDIR user with parameter user_id: {user_id}")
    idim_proxy_api = IdimProxyService(requester)
    search_result = idim_proxy_api.search_idir({user_id: user_id})
    return search_result