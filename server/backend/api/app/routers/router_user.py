import logging
from http import HTTPStatus

from api.app import database
from api.app.crud import crud_user
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.app.schemas import FamUserUpdateResponseSchema

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.put(
    "/users-information",
    status_code=HTTPStatus.OK,
    response_model=FamUserUpdateResponseSchema,
)
def update_user_information_from_idim_source(
    page: int = 1,
    per_page: int = 100,
    use_pagination: bool = False,
    db: Session = Depends(database.get_db),
):
    """
    Call IDIM web service to grab latest user information and update records in FAM database for IDIR and Business BCeID users
    """
    LOGGER.debug("Updating database user information")

    response = crud_user.update_user_info_from_idim_source(
        db, use_pagination, page, per_page
    )

    LOGGER.debug("Updating database user information is done")

    return response
