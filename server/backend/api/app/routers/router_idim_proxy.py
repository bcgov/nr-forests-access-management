import logging

from api.app.integration.idim_proxy import IdimProxyService
from api.app.routers.router_guards import (get_current_requester,
                                           internal_only_action)
from api.app.schemas import IdimProxyIdirInfo, IdimProxySearchParamIdir
from fastapi import APIRouter, Depends, Query

ERROR_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"

LOGGER = logging.getLogger(__name__)

router = APIRouter()

@router.get("/idir", response_model=IdimProxyIdirInfo, dependencies=[Depends(internal_only_action)])
def idir_search(
    user_id: str = Query(max_length=15),
    # user_id: str = Annotated[str, Query(max_length=15)], # Although 'Annotated' is recommended by FastAPI, however, using Annotated has a bug
                                                           # It will throw pydantic.error_wrappers.ValidationError which is 500, not 422 we need.
                                                           # known issue: https://github.com/tiangolo/fastapi/issues/4974
                                                           # Fallback to use Query only.
    requester=Depends(get_current_requester)
):
    LOGGER.debug(f"Searching IDIR user with parameter user_id: {user_id}")
    idim_proxy_api = IdimProxyService(requester)
    search_result = idim_proxy_api.search_idir(
        IdimProxySearchParamIdir(**{
            "userId": user_id
        })
    )
    idir_info = IdimProxyIdirInfo.from_api_json(search_result)
    idir_info.userId = user_id if not idir_info.found else idir_info.userId
    return idir_info