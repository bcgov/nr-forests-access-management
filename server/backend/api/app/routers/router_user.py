import logging
from http import HTTPStatus

from api.app import database
from api.app.constants import ApiInstanceEnv
from api.app.crud import crud_user
from api.app.routers.router_guards import (get_current_requester,
                                           internal_only_action,
                                           verify_api_key_for_update_user_info)
from api.app.schemas import FamUserUpdateResponseSchema
from api.app.schemas.requester import RequesterSchema
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.put(
    "/users-information",
    status_code=HTTPStatus.OK,
    response_model=FamUserUpdateResponseSchema,
    dependencies=[
        Depends(verify_api_key_for_update_user_info),
        Depends(internal_only_action)
    ],
)
def update_user_information_from_idim_source(
    page: int = 1,
    per_page: int = 100,
    use_pagination: bool = False,
    use_env: ApiInstanceEnv = ApiInstanceEnv.PROD,
    db: Session = Depends(database.get_db),
    requester: RequesterSchema = Depends(get_current_requester)
):
    """
    Call IDIM web service to grab latest user information and update records in FAM database for IDIR and Business BCeID users
    """
    LOGGER.debug("Updating database user information")

    response = crud_user.update_user_info_from_idim_source(
        db, requester, use_pagination, page, per_page, use_env
    )

    LOGGER.debug("Updating database user information is done")

    return response
