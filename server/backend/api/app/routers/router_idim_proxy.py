import logging
from typing import Annotated

from api.app.constants import IdimSearchUserParamType, ApiInstanceEnv
from api.app.decorators.endpoint_timing_dec import endpoint_timing_dec
from api.app.integration.idim_proxy import IdimProxyService
from api.app.routers.router_guards import get_current_requester, internal_only_action
from api.app.routers.router_utils import get_api_instance_env
from api.app.schemas import (
    IdimProxyBceidInfoSchema,
    IdimProxyBceidSearchParamSchema,
    IdimProxyIdirInfoSchema,
    IdimProxySearchParamSchema,
)
from api.app.schemas.requester import RequesterSchema
from api.app.schemas.idim_proxy_idir_users_search import (
    IdimProxyIdirUsersSearchParamReqSchema,
    IdimProxyIdirUsersSearchResSchema,
)
from fastapi import APIRouter, Depends, Query

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/idir",
    response_model=IdimProxyIdirInfoSchema,
    dependencies=[Depends(internal_only_action)],
    summary="Lookup IDIR user",
    description="Lookup an IDIR user by user ID.",
)
def idir_lookup(
    user_id: Annotated[str, Query(max_length=20)],
    requester: Annotated[RequesterSchema, Depends(get_current_requester)],
    api_instance_env: Annotated[ApiInstanceEnv, Depends(get_api_instance_env)],
):
    LOGGER.debug(f"Searching IDIR user with parameter user_id: {user_id}")
    idim_proxy_api = IdimProxyService(requester, api_instance_env)
    search_result = idim_proxy_api.lookup_idir(
        IdimProxySearchParamSchema(**{"userId": user_id})
    )
    return search_result


@router.get(
    "/bceid",
    response_model=IdimProxyBceidInfoSchema,
    summary="Lookup BCEID user",
    description="Lookup a BCeID Business user by user ID.",
)
def bceid_lookup(
    user_id: Annotated[str, Query(max_length=20)],
    requester: Annotated[RequesterSchema, Depends(get_current_requester)],
    api_instance_env: Annotated[ApiInstanceEnv, Depends(get_api_instance_env)],
):
    LOGGER.debug(f"Searching BCEID user with parameter user_id: {user_id}")
    idim_proxy_api = IdimProxyService(requester, api_instance_env)
    search_result = idim_proxy_api.lookup_business_bceid(
        IdimProxyBceidSearchParamSchema(
            **{"searchUserBy": IdimSearchUserParamType.USER_ID, "searchValue": user_id}
        )
    )
    return search_result


@router.get(
    "/users/idir/search",
    response_model=IdimProxyIdirUsersSearchResSchema,
    status_code=200,
    summary="Search IDIR users",
    description="Search for IDIR users.",
)
@endpoint_timing_dec("fam-search_idir_users")
def search_idir_users(
    search_params: Annotated[IdimProxyIdirUsersSearchParamReqSchema, Depends()],
    requester: Annotated[RequesterSchema, Depends(get_current_requester)],
    api_instance_env: Annotated[ApiInstanceEnv, Depends(get_api_instance_env)],
):
    """
    FAM-side API for admins to search IDIR users through IDIM Proxy.
    """
    LOGGER.info(
        "FAM API - searching IDIR users by requester=%s (id=%s)",
        requester.user_name,
        requester.user_id,
    )

    idim_proxy_api = IdimProxyService(requester, api_instance_env)
    return idim_proxy_api.search_idir_users(search_params)