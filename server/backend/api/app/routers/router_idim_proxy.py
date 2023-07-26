import logging
from typing import List

from api.app.integration.idim_proxy import IdimProxyService
from api.app.requester import (Requester, get_current_requester,
                               internal_only_action)
from api.app.schemas import IdimProxySearchParamIdir
from fastapi import APIRouter, Depends, Query

ERROR_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"

LOGGER = logging.getLogger(__name__)

router = APIRouter()

@router.get("/idir", response_model=dict, dependencies=[Depends(internal_only_action)])
def idir_search(
    user_id: str,
    requester=Depends(get_current_requester)
):
    LOGGER.debug(f"Searching IDIR user with parameter user_id: {user_id}")
    idim_proxy_api = IdimProxyService(requester)
    search_result = idim_proxy_api.search_idir(
        IdimProxySearchParamIdir(**{
            "userId": user_id
        })
    )
    return search_result