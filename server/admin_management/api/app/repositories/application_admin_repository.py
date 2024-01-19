import logging
from typing import List

from api.app.models.model import FamApplicationAdmin
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class ApplicationAdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_application_admins(self) -> List[FamApplicationAdmin]:
        return (
            self.db
            .query(FamApplicationAdmin)
            .order_by(
                FamApplicationAdmin.user_id,
                FamApplicationAdmin.application_id
            )
            .all()
        )

    def get_application_admin_by_app_and_user_id(
        self, application_id: int, user_id: int
    ) -> FamApplicationAdmin:
        return (
            self.db.query(FamApplicationAdmin)
            .filter(
                FamApplicationAdmin.application_id == application_id,
                FamApplicationAdmin.user_id == user_id,
            )
            .one_or_none()
        )

    def get_application_admin_by_id(
        self, application_admin_id: int
    ) -> FamApplicationAdmin:
        return (
            self.db.query(FamApplicationAdmin)
            .filter(
                FamApplicationAdmin.application_admin_id == application_admin_id
            )
            .one_or_none()
        )

    def get_application_admin_by_application_id(
        self, application_id: int
    ) -> List[FamApplicationAdmin]:
        return (
            self.db.query(FamApplicationAdmin)
            .filter(
                FamApplicationAdmin.application_id == application_id
            )
            .all()
        )

    def create_application_admin(
        self, application_id: int, user_id: int, requester: str
    ) -> FamApplicationAdmin:
        new_fam_application_admin: FamApplicationAdmin = (
            FamApplicationAdmin(
                **{
                    "user_id": user_id,
                    "application_id": application_id,
                    "create_user": requester,
                }
            )
        )
        self.db.add(new_fam_application_admin)
        self.db.flush()
        self.db.refresh(new_fam_application_admin)
        LOGGER.debug(
            f"New FamApplicationAdmin added for {new_fam_application_admin.__dict__}"
        )
        return new_fam_application_admin

    def delete_application_admin(self, application_admin_id: int):
        record = (
            self.db.query(FamApplicationAdmin)
            .filter(
                FamApplicationAdmin.application_admin_id == application_admin_id
            )
            .one()
        )
        self.db.delete(record)
        self.db.flush()
