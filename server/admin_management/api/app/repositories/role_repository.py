import logging
from sqlalchemy.orm import Session

from api.app.models import model as models


LOGGER = logging.getLogger(__name__)


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_role(self, role_id: str) -> models.FamRole:
        return (
            self.db.query(models.FamRole)
            .filter(models.FamRole.role_id == role_id)
            .one_or_none()
        )

    def get_role_by_role_name_and_app_id(
        self, role_name: str, application_id: int
    ) -> models.FamRole:
        return (
            self.db.query(models.FamRole)
            .filter(
                models.FamRole.role_name == role_name,
                models.FamRole.application_id == application_id,
            )
            .one_or_none()
        )

    def create_role(self, fam_role: models.FamRole) -> models.FamRole:
        self.db.add(fam_role)
        self.db.flush()
        return fam_role
