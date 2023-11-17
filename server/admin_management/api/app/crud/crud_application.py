import logging

from sqlalchemy.orm import Session

from api.app.models import model as models

from . import crud_utils as crud_utils

LOGGER = logging.getLogger(__name__)


def get_application(db: Session, application_id: int):
    """gets a single application"""
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_id == application_id)
        .one_or_none()
    )
    return application