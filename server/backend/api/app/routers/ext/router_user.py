import logging

from api.app import database
from api.app.crud import crud_utils
from api.app.crud.services import ext_app_user_search_service
from api.app.decorators.endpoint_timing_dec import endpoint_timing_dec
from api.app.integration.idim_proxy import IdimProxyService
from api.app.routers.router_guards import (authorize_ext_api_by_app_role,
                       get_current_requester)
from api.app.schemas.ext.pagination import (ExtUserSearchPagedResultsSchema,
                                            ExtUserSearchParamSchema)
from api.app.schemas.ext.user_search import (ExtApplicationUserSearchGetSchema,
                         ExtApplicationUserSearchSchema,
                         ExtIdirUserSearchParamSchema)
from api.app.schemas.fam_application import FamApplicationSchema
from api.app.schemas.idim_proxy_idir_users_search import (
    IdimProxyIdirUsersSearchParamReqSchema,
    IdimProxyIdirUsersSearchResSchema,
)
from api.app.schemas.requester import RequesterSchema
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    response_model=ExtUserSearchPagedResultsSchema[ExtApplicationUserSearchGetSchema],
    status_code=200
)
def user_search(
    db: Session = Depends(database.get_db),
    requester: RequesterSchema = Depends(get_current_requester),
    page_params: ExtUserSearchParamSchema = Depends(),
    filter_params: ExtApplicationUserSearchSchema = Depends(),
    application: FamApplicationSchema = Depends(authorize_ext_api_by_app_role)
):
    """
    External API to search users information (in FAM) associated with an application.
    See API spec at https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Users+Search+API
    """
    LOGGER.debug(
        f"Expernal API - searching users for filter_params: {filter_params}, "
        f"and page_params: {page_params}, "
        f"by requester: {requester.user_name} (id: {requester.user_id})"
    )

    service = ext_app_user_search_service.ExtAppUserSearchService(
        db=db,
        requester=requester,
        application_id=application.application_id
    )

    paged_results = service.search_users(
        page_params=page_params,
        filter_params=filter_params
    )

    return paged_results


### --- Below is the lookup/search through IDIM Proxy API for users. Not to the FAM database 'user'.

@router.get(
    "/identity/idir/search",
    response_model=IdimProxyIdirUsersSearchResSchema,
    status_code=200,
)
@endpoint_timing_dec("external-search_idir_users")
def search_idir_users(
    search_params: ExtIdirUserSearchParamSchema = Depends(),
    requester: RequesterSchema = Depends(get_current_requester),
    application: FamApplicationSchema = Depends(authorize_ext_api_by_app_role),
) -> IdimProxyIdirUsersSearchResSchema:
    """
    External API for downstream applications to search IDIR users.
    """
    LOGGER.info(
        "External API - searching IDIR users by requester=%s (id=%s), app=%s",
        requester.user_name,
        requester.user_id,
        application.application_name,
    )

    idim_search_params = IdimProxyIdirUsersSearchParamReqSchema(
        firstName=search_params.first_name,
        lastName=search_params.last_name,
        userId=search_params.user_id,
        firstNameMatchMode=search_params.first_name_match_mode,
        lastNameMatchMode=search_params.last_name_match_mode,
        userIdMatchMode=search_params.user_id_match_mode,
        pageSize=search_params.page_size,
    )

    api_instance_env = crud_utils.use_api_instance_by_app(application)
    idim_proxy_api = IdimProxyService(
        requester=requester,
        api_instance_env=api_instance_env,
    )
    return idim_proxy_api.search_idir_users(idim_search_params)