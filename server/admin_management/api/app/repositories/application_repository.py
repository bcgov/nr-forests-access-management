import logging
from typing import List

from api.app.models.model import FamApplication
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_applications(self) -> List[FamApplication]:
        return (
            self.db.query(FamApplication)
            .order_by(FamApplication.application_id)
            .all()
        )

    def get_application(self, application_id: int) -> FamApplication:
        return (
            self.db.query(FamApplication)
            .filter(FamApplication.application_id == application_id)
            .one_or_none()
        )
