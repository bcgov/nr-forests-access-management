
import logging

from api.app import database
from api.app.constants import ApiInstanceEnv, AppEnv
from api.app.crud import crud_application
from api.config import config
from fastapi import Depends
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


def get_app_environment(
    application_id,
    db: Session = Depends(database.get_db),
) -> AppEnv:
    application_id = 1
    application = crud_application.get_application(application_id=application_id, db=db)
    return application.app_environment


def get_api_instance_env(
    app_environment=Depends(get_app_environment)
) -> ApiInstanceEnv:
    return config.use_api_instance_by_app_env(app_environment)