import logging
from typing import List

from api.app.models.model import FamAccessControlPrivilege, FamRole
from api.app.schemas import FamAccessControlPrivilegeCreateDto
from sqlalchemy.orm import Session, joinedload

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

    def create_access_control_privilege(
        self, fam_access_control_priviliege: FamAccessControlPrivilegeCreateDto
    ) -> FamAccessControlPrivilege:
        access_control_priviliege_dict = fam_access_control_priviliege.model_dump()
        db_item = FamAccessControlPrivilege(**access_control_priviliege_dict)
        self.db.add(db_item)
        self.db.flush()
        self.db.refresh(db_item)
        return db_item

    def get_user_delegated_admin_grants(self, user_id: int) -> List[FamRole]:
        """
        Find out from `app_fam.fam_access_control_privilege` the applications
            and roles being granted for the user.

        :param user_id: primary id that is associated with the user.
        :return: List of "roles" granted for the user or None.
        """
        return (
            self.db.query(FamRole)
                .options(joinedload(FamRole.application))  # also loads relationship
                .select_from(FamAccessControlPrivilege)
                .join(FamAccessControlPrivilege.role)
                .join(FamAccessControlPrivilege.user)
                .filter(FamAccessControlPrivilege.user_id == user_id)
                .order_by(FamRole.application_id, FamRole.role_id)
                .all()
        )
