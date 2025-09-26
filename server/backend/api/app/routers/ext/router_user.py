import logging

from api.app import database
from api.app.routers.router_guards import (authorize_ext_api_by_app_role,
                                           get_current_requester)
from api.app.schemas.ext.pagination import (ExtUserSearchPagedResultsSchema,
                                            ExtUserSearchParamSchema)
from api.app.schemas.ext.user_search import (ExtApplicationUserSearchGetSchema,
                                             ExtApplicationUserSearchSchema)
from api.app.schemas.fam_application import FamApplicationSchema
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
    External API to search users information associated with an application.
    See API spec at https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Users+Search+API
    """
    LOGGER.debug(
        f"Expernal API - searching users for filter_params: {filter_params}, "
        f"and page_params: {page_params}, "
        f"by requester: {requester.user_name} (id: {requester.user_id})"
    )
    # TODO... implement the search logic here.
    # paged_results = crud_application.get_application_role_assignments(
    #     db=db, application_id=application_id, requester=requester, page_params=page_params
    # )

    return None
