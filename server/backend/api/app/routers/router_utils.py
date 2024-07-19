import logging
from fastapi import Depends
from sqlalchemy.orm import Session

from api.app import database
from api.app.constants import ApiInstanceEnv
from api.app.crud import crud_utils, crud_application


LOGGER = logging.getLogger(__name__)


def get_api_instance_env(
    application_id: int, db: Session = Depends(database.get_db)
) -> ApiInstanceEnv:
    application = crud_application.get_application(db, application_id)
    return crud_utils.use_api_instance_by_app(application)
