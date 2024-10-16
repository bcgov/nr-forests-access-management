import logging
from typing import List

from api.app.models.model import FamRole
from api.app.schemas.schemas import FamRoleCreateDto
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_role_by_id(self, role_id: str) -> FamRole:
        return self.db.get(FamRole, role_id)

    def get_base_roles_by_app_id(self, application_id: str) -> List[FamRole]:
        """
        Only obtain the base roles, not the child roles. For example, this
        `FOM_SUBMITTER_00001011` will be filtered out (it is a child role of
        `FOM_SUBMITTER` role).
        """
        return (
            self.db.query(FamRole)
            # Query below when compare to `None` needs to use parent_role_id == None,
            # using `is None` doesn't translate to the correct query in sqlalchemy
            .filter(
                FamRole.application_id == application_id,
                FamRole.parent_role_id == None # noqa
            )
            .order_by(FamRole.role_id)
            .all()
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

    def create_role(self, fam_role: FamRoleCreateDto) -> FamRole:
        db_item = FamRole(**fam_role)
        self.db.add(db_item)
        self.db.flush()
        return db_item
