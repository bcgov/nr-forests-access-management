import logging

from api.app.constants import IdimSearchUserParamType, ApiInstanceEnv
from api.app.integration.idim_proxy import IdimProxyService
from api.app.routers.router_guards import get_current_requester, internal_only_action
from api.app.routers.router_utils import get_api_instance_env
from api.app.schemas import (
    IdimProxyBceidInfoSchema,
    IdimProxyBceidSearchParamSchema,
    IdimProxyIdirInfoSchema,
    IdimProxySearchParamSchema,
)
from fastapi import APIRouter, Depends, Query

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/idir",
    response_model=IdimProxyIdirInfoSchema,
    dependencies=[Depends(internal_only_action)],
)
def idir_search(
    user_id: str = Query(max_length=20),
    # user_id: str = Annotated[str, Query(max_length=15)], # Although 'Annotated' is recommended by FastAPI, however, using Annotated has a bug
    # It will throw pydantic.error_wrappers.ValidationError which is 500, not 422 we need.
    # known issue: https://github.com/tiangolo/fastapi/issues/4974
    # Fallback to use Query only.
    requester=Depends(get_current_requester),
    api_instance_env: ApiInstanceEnv = Depends(get_api_instance_env),
):
    LOGGER.debug(f"Searching IDIR user with parameter user_id: {user_id}")
    idim_proxy_api = IdimProxyService(requester, api_instance_env)
    search_result = idim_proxy_api.search_idir(
        IdimProxySearchParamSchema(**{"userId": user_id})
    )
    return search_result


# TODO later change this to "/business_bceid"
@router.get("/bceid", response_model=IdimProxyBceidInfoSchema)
def bceid_search(
    user_id: str = Query(max_length=20),
    requester=Depends(get_current_requester),
    api_instance_env: ApiInstanceEnv = Depends(get_api_instance_env),
):
    LOGGER.debug(f"Searching BCEID user with parameter user_id: {user_id}")
    idim_proxy_api = IdimProxyService(requester, api_instance_env)
    search_result = idim_proxy_api.search_business_bceid(
        IdimProxyBceidSearchParamSchema(
            **{"searchUserBy": IdimSearchUserParamType.USER_ID, "searchValue": user_id}
        )
    )
    return search_result
