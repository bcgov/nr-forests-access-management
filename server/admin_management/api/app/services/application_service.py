import logging
from sqlalchemy.orm import Session

from api.app.repositories.application_repository import ApplicationRepository


LOGGER = logging.getLogger(__name__)


class ApplicationService:
    def __init__(self, db: Session):
        self.application_repo = ApplicationRepository(db)

    def get_application(self, application_id: int):
        return self.application_repo.get_application(application_id)

