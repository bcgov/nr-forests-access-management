import logging
from sqlalchemy.orm import Session

from api.app.models import model as models


LOGGER = logging.getLogger(__name__)


class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_application(self, application_id: int) -> models.FamApplication:
        return (
            self.db.query(models.FamApplication)
            .filter(models.FamApplication.application_id == application_id)
            .one_or_none()
        )
