import logging
from http import HTTPStatus
from typing import Annotated

from api.app import database
from api.app import constants as fam_constants
from api.app.crud import crud_application, crud_user_role, crud_utils
from api.app.crud.services import ext_app_user_search_service
from api.app.decorators.endpoint_timing_dec import endpoint_timing_dec
from api.app.integration.idim_proxy import IdimProxyService
from api.app.jwt_validation import get_request_app_client_id
from api.app.routers.router_guards import (authorize_ext_api_by_app_role,
                       get_current_requester)
from api.app.schemas.ext.pagination import (ExtUserSearchPagedResultsSchema,
                                            ExtUserSearchParamSchema)
from api.app.schemas.ext.user_role_metadata import (
    ExtUserRoleMetadataResponseSchema,
    ExtUserRoleMetadataRoleSchema,
)
from api.app.schemas.ext.user_search import (ExtApplicationUserSearchGetSchema,
                         ExtApplicationUserSearchSchema,
                         ExtIdirUserSearchParamSchema)
from api.app.schemas.fam_application import FamApplicationSchema
from api.app.schemas.idim_proxy_idir_users_search import (
    IdimProxyIdirUsersSearchParamReqSchema,
    IdimProxyIdirUsersSearchResSchema,
)
from api.app.schemas.requester import RequesterSchema
from api.app.utils import utils
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.app.routers.router_utils import map_user_type_to_idp_type

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    response_model=ExtUserSearchPagedResultsSchema[ExtApplicationUserSearchGetSchema],
    status_code=200,
    summary="Search FAM users",
    description="Search FAM users information associated with an application."
)
def user_search(
    db: Annotated[Session, Depends(database.get_db)],
    requester: Annotated[RequesterSchema, Depends(get_current_requester)],
    page_params: Annotated[ExtUserSearchParamSchema, Depends()],
    filter_params: Annotated[ExtApplicationUserSearchSchema, Depends()],
    application: Annotated[
        FamApplicationSchema,
        Depends(authorize_ext_api_by_app_role),
    ],
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


### --- Below is the search through IDIM Proxy API for users. Not to the FAM database 'user'.

@router.get(
    "/identity/idir/search",
    response_model=IdimProxyIdirUsersSearchResSchema,
    status_code=200,
    summary="Search IDIR users",
    description="Search IDIR users identity through IDIM.",
)
@endpoint_timing_dec("external-search_idim_idir_users")
def search_idim_idir_users(
    search_params: Annotated[ExtIdirUserSearchParamSchema, Depends()],
    requester: Annotated[RequesterSchema, Depends(get_current_requester)],
    application: Annotated[
        FamApplicationSchema,
        Depends(authorize_ext_api_by_app_role),
    ],
):
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
        pageSize=search_params.page_size,
    )

    api_instance_env = crud_utils.use_api_instance_by_app(application)
    idim_proxy_api = IdimProxyService(
        requester=requester,
        api_instance_env=api_instance_env,
    )
    return idim_proxy_api.search_idir_users(idim_search_params)


@router.get(
    "/me/role-metadata",
    response_model=ExtUserRoleMetadataResponseSchema,
    status_code=200,
    summary="Get current user role metadata",
    description="Get role metadata for the authenticated user within the application context.",
)
def get_current_user_role_metadata(
    db: Annotated[Session, Depends(database.get_db)],
    requester: Annotated[RequesterSchema, Depends(get_current_requester)],
    app_client_id: Annotated[str, Depends(get_request_app_client_id)],  # Cognito app client for the application.
):
    """Return current requester role metadata scoped to application from JWT."""
    application = crud_application.get_application_by_app_client_id(db, app_client_id)
    if not application:
        utils.raise_http_exception(
            status_code=HTTPStatus.FORBIDDEN,
            error_code=fam_constants.ERROR_CODE_INVALID_OPERATION,
            error_msg=(
                "Token contains invalid application client id "
                f"{utils.mask_string(app_client_id, 5)}"
            ),
        )

    role_assignments = crud_user_role.get_user_roles_by_cognito_id_and_app_id(
        db=db,
        cognito_user_id=requester.cognito_user_id,
        application_id=application.application_id,
    )

    roles = [
        ExtUserRoleMetadataRoleSchema(
            role_name=assignment.role.role_name,
            display_name=assignment.role.display_name,
            expiry_date=assignment.expiry_date.replace(microsecond=0) if assignment.expiry_date else None,
            forest_client_number=(
                assignment.role.forest_client_relation.forest_client_number
                if assignment.role.forest_client_relation
                else None
            ),
        )
        for assignment in role_assignments
    ]

    return ExtUserRoleMetadataResponseSchema(
        user_name=requester.user_name,
        domain=map_user_type_to_idp_type(requester.user_type_code),
        roles=roles,
    )