import logging
from sqlalchemy.orm import Session

from api.app.models import model as models


LOGGER = logging.getLogger(__name__)


class AccessControlPrivilegeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_use_role_by_user_id_and_role_id(
        self, user_id: int, role_id: int
    ) -> models.FamAccessControlPrivilege:
        return (
            self.db.query(models.FamAccessControlPrivilege)
            .filter(
                models.FamAccessControlPrivilege.user_id == user_id,
                models.FamAccessControlPrivilege.role_id == role_id,
            )
            .one_or_none()
        )

    def create_access_control_privilege(
        self, user_id: int, role_id: int, requester: str
    ) -> models.FamAccessControlPrivilege:
        new_fam_access_control_privilege: models.FamAccessControlPrivilege = (
            models.FamAccessControlPrivilege(
                **{
                    "user_id": user_id,
                    "role_id": role_id,
                    "create_user": requester,
                }
            )
        )
        self.db.add(new_fam_access_control_privilege)
        self.db.flush()
        self.db.refresh(new_fam_access_control_privilege)
        return new_fam_access_control_privilege
