import logging
from typing import List

from api.app.models.model import FamApplication, FamApplicationAdmin, FamUser
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class ApplicationAdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_application_admins(self) -> List[FamApplicationAdmin]:
        return (
            self.db.query(FamApplicationAdmin)
            .order_by(FamApplicationAdmin.user_id, FamApplicationAdmin.application_id)
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
            .filter(FamApplicationAdmin.application_admin_id == application_admin_id)
            .one_or_none()
        )

    def create_application_admin(
        self, application_id: int, user_id: int, requester_cognito_user_id: str
    ) -> FamApplicationAdmin:
        new_fam_application_admin = FamApplicationAdmin(
            **{
                "user_id": user_id,
                "application_id": application_id,
                "create_user": requester_cognito_user_id,
            }
        )
        self.db.add(new_fam_application_admin)
        self.db.flush()
        self.db.refresh(new_fam_application_admin)
        LOGGER.debug(
            f"New FamApplicationAdmin added for {new_fam_application_admin.__dict__}"
        )
        return new_fam_application_admin

    def delete_application_admin(self, application_admin_id: int) -> FamApplicationAdmin:
        record = (
            self.db.query(FamApplicationAdmin)
            .filter(FamApplicationAdmin.application_admin_id == application_admin_id)
            .one()
        )
        self.db.delete(record)
        self.db.flush()
        return record

    def get_user_app_admin_grants(self, user_id: int) -> List[FamApplication]:
        """
        Find out from `app_fam.fam_application_admin` the applications
            being granted for the user; including "FAM" application.

        Filter on: Only 'IDIR' type user can be an Application Admin.

        :param user_id: primary id that is associated with the user.
        :return: List of "applications" the user is admin of or None.
        """
        return (
            self.db.query(FamApplication)
            .select_from(FamApplicationAdmin)
            .join(FamApplicationAdmin.application)
            .join(FamApplicationAdmin.user)
            .filter(FamApplicationAdmin.user_id == user_id)
            .order_by(FamApplication.application_id)
            .all()
        )

    def get_application_admins_by_application_id(
        self, application_id: int, user_id: int = None
    ) -> List[FamApplicationAdmin]:
        """
        Get all application admins for a specific application.
        Optionally exclude the current user from the results.

        :param application_id: The application ID to get admins for.
        :param user_id: Optional user ID to exclude from results.
        :return: List of FamApplicationAdmin for the specified application.
        """
        query = (
            self.db.query(FamApplicationAdmin)
            .filter(FamApplicationAdmin.application_id == application_id)
        )

        if user_id:
            query = query.filter(FamApplicationAdmin.user_id != user_id)

        return query.order_by(FamApplicationAdmin.user_id).all()
