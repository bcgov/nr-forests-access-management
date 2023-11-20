import logging
from sqlalchemy.orm import Session

from api.app.models import model as models


LOGGER = logging.getLogger(__name__)


class ApplicationAdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_application_admin(
        self, application_id: int, user_id: int, requester: str
    ) -> models.FamApplicationAdmin:
        new_fam_application_admin: models.FamApplicationAdmin = (
            models.FamApplicationAdmin(
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

    def get_application_admin(
        self, application_id: int, user_id: int
    ) -> models.FamApplicationAdmin:
        return (
            self.db.query(models.FamApplicationAdmin)
            .filter(
                models.FamApplicationAdmin.application_id == application_id,
                models.FamApplicationAdmin.user_id == user_id,
            )
            .one_or_none()
        )

    def get_application_admin_by_id(
        self, application_admin_id: int
    ) -> models.FamApplicationAdmin:
        return (
            self.db.query(models.FamApplicationAdmin)
            .filter(
                models.FamApplicationAdmin.application_admin_id == application_admin_id
            )
            .one_or_none()
        )

    def delete_application_admin(self, application_admin_id: int):
        record = (
            self.db.query(models.FamApplicationAdmin)
            .filter(models.FamApplicationAdmin.application_admin_id == application_admin_id)
            .one()
        )
        self.db.delete(record)
        self.db.flush()