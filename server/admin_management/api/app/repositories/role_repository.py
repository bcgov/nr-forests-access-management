import logging
from sqlalchemy.orm import Session

from api.app import schemas
from api.app.models.model import FamRole


LOGGER = logging.getLogger(__name__)


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_role_by_id(self, role_id: str) -> FamRole:
        return (
            self.db.query(FamRole)
            .filter(FamRole.role_id == role_id)
            .one_or_none()
        )

    def get_role_by_role_name_and_app_id(
        self, role_name: str, application_id: int
    ) -> FamRole:
        return (
            self.db.query(FamRole)
            .filter(
                FamRole.role_name == role_name,
                FamRole.application_id == application_id,
            )
            .one_or_none()
        )

    def create_role(self, fam_role: schemas.FamRoleCreate) -> FamRole:
        db_item = FamRole(**fam_role)
        self.db.add(db_item)
        self.db.flush()
        return db_item
