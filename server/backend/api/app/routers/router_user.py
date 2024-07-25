import logging
from http import HTTPStatus

from api.app import database
from api.app.crud import crud_user
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.app.models.model import FamUser

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    status_code=HTTPStatus.OK,
)
def update_user_information_from_idim_source(
    db: Session = Depends(database.get_db),
):
    """
    Call IDIM web service to grab latest user information and update the record in FAM database
    """
    LOGGER.debug(f"Updating datanase user information")

    crud_user.update_user_info_from_idim_source(db)
    LOGGER.debug(f"Updating datanase user information is done")
