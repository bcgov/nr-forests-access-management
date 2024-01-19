import logging
from sqlalchemy.orm import Session

from api.app import schemas
from api.app.models.model import FamAccessControlPrivilege


LOGGER = logging.getLogger(__name__)


class AccessControlPrivilegeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id_and_role_id(
        self, user_id: int, role_id: int
    ) -> FamAccessControlPrivilege:
        return (
            self.db.query(FamAccessControlPrivilege)
            .filter(
                FamAccessControlPrivilege.user_id == user_id,
                FamAccessControlPrivilege.role_id == role_id,
            )
            .one_or_none()
        )

    def get_by_id(self, access_control_privilege_id: int) -> FamAccessControlPrivilege:
        return (
            self.db.query(FamAccessControlPrivilege)
            .filter(
                FamAccessControlPrivilege.access_control_privilege_id
                == access_control_privilege_id
            )
            .one_or_none()
        )

    def create_access_control_privilege(
        self, fam_access_control_priviliege: schemas.FamAccessControlPrivilegeCreate
    ) -> FamAccessControlPrivilege:
        db_item = FamAccessControlPrivilege(**fam_access_control_priviliege)
        self.db.add(db_item)
        self.db.flush()
        self.db.refresh(db_item)
        return db_item
