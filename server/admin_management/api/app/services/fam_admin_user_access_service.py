import logging

from api.app.constants import APPLICATION_FAM
from api.app.repositories.access_control_privilege_repository import \
    AccessControlPrivilegeRepository
from api.app.repositories.application_admin_repository import \
    ApplicationAdminRepository
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class FamAdminUserAccessService:
    def __init__(self, db: Session):
        self.application_admin_repo = ApplicationAdminRepository(db)
        self.access_control_privilege_repo = AccessControlPrivilegeRepository(db)

    def get_access_grants(self, user_id: int):
        """
        Find out access (FAM_ADMIN, APP_ADMIN, DELEGATED_ADMIN) granted
        for the user.

        :param user_id: primary id that is associated with the user.
        :return: List of admin grants for the user or None.
        """
        user_all_admin_grants = self.application_admin_repo \
            .get_user_app_admin_grants(user_id)

        # FAM_ADMIN
        fam_admin_grants = [
            granted_app for granted_app in user_all_admin_grants
            if granted_app.application_name == APPLICATION_FAM
        ]

        # APP_ADMIN (apps other than FAM)
        apps_admin_grants = [
            granted_app for granted_app in user_all_admin_grants
            if granted_app.application_name != APPLICATION_FAM
        ]

        # DELEGATED_ADMIN
        delegated_admin_grants = self.access_control_privilege_repo \
            .get_user_delegated_admin_grants(user_id)

        return delegated_admin_grants # TODO, return correct schema

