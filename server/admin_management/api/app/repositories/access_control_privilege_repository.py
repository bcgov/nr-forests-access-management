import logging
from sqlalchemy.orm import Session
from typing import List

from api.app.schemas import FamAccessControlPrivilegeCreateDto
from api.app.models.model import FamAccessControlPrivilege, FamRole


LOGGER = logging.getLogger(__name__)


class AccessControlPrivilegeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_acp_by_user_id_and_role_id(
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

    def get_acp_by_id(
        self, access_control_privilege_id: int
    ) -> FamAccessControlPrivilege:
        return self.db.get(FamAccessControlPrivilege, access_control_privilege_id)

    def get_acp_by_application_id(
        self, application_id: int
    ) -> List[FamAccessControlPrivilege]:
        return (
            self.db.query(FamAccessControlPrivilege)
            .join(FamRole)
            .filter(FamRole.application_id == application_id)
            .all()
        )

    def create_access_control_privilege(
        self, fam_access_control_priviliege: FamAccessControlPrivilegeCreateDto
    ) -> FamAccessControlPrivilege:
        access_control_priviliege_dict = fam_access_control_priviliege.model_dump()
        db_item = FamAccessControlPrivilege(**access_control_priviliege_dict)
        self.db.add(db_item)
        self.db.flush()
        self.db.refresh(db_item)
        return db_item
