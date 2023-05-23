import logging

from typing import List
from api.app.crud import crud_application
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from .. import database
from api.app.models import model as models


LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", status_code=200)
def get_applications(
    response: Response,
    db: Session = Depends(database.get_db),
):

    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    fam_apps = db.query(models.FamApplication).all()
    if len(fam_apps) == 0:
        response.status_code = 204
    return response

