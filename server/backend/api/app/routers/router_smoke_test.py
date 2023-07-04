import logging

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from .. import database
from api.app.models import model as models


LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", status_code=200)
def smoke_test(
    response: Response,
    db: Session = Depends(database.get_db),
):

    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")

    try:
        fam_apps = db.query(models.FamApplication).all()
        if len(fam_apps) == 0:
            response.status_code = 417
        else:
            response.status_code = 200
        return response

    except Exception as e:
        LOGGER.exception(e)
        raise e



