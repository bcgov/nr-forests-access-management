import itertools
import logging
from typing import List

from api.app.constants import APPLICATION_FAM, AdminRoleAuthGroup
from api.app.models.model import FamApplication, FamRole
from api.app.repositories.access_control_privilege_repository import \
    AccessControlPrivilegeRepository
from api.app.repositories.application_admin_repository import \
    ApplicationAdminRepository
from api.app.repositories.application_repository import ApplicationRepository
from api.app.repositories.role_repository import RoleRepository
from api.app.schemas import (FamApplicationDto, FamAuthGrant, FamGrantDetail,
                             FamRoleDto)
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class FamAdminUserAccessService:
    def __init__(self, db: Session):
        self.application_admin_repo = ApplicationAdminRepository(db)
        self.access_control_privilege_repo = AccessControlPrivilegeRepository(db)
        self.application_repo = ApplicationRepository(db)
        self.role_repo = RoleRepository(db)

    def get_access_grants(self, user_id: int):
        """
        Find out access (FAM_ADMIN, APP_ADMIN, DELEGATED_ADMIN) granted
        for the user.

        :param user_id: primary id that is associated with the user.
        :return: List of admin grants for the user or None.
        """
        # FamApplication(s) granted for Admin user (FAM and others).
        user_admin_privilege = self.application_admin_repo \
            .get_user_app_admin_grants(user_id)

        # FamApplication(s) granted for APP_ADMIN (apps filtered)
        user_apps_admin_privilege = [
            granted_app for granted_app in user_admin_privilege
            if granted_app.application_name != APPLICATION_FAM
        ]

        # FamRole(s) granted for user as DELEGATED_ADMIN
        user_delegated_admin_privilege = self.access_control_privilege_repo \
            .get_user_delegated_admin_grants(8)
        # .get_user_delegated_admin_grants(user_id)

        user_access_grants = []
        is_user_fam_admin = len(list(filter(
            lambda grant: grant.application_name == APPLICATION_FAM,
            user_admin_privilege))) != 0
        if is_user_fam_admin:
            user_access_grants.append(self.__construct_fam_admin_auth_grant())

        is_user_app_admin = len(user_apps_admin_privilege) != 0
        if is_user_app_admin:
            user_access_grants.append(self.__construct_app_admin_auth_grant(
                user_apps_admin_privilege
            ))

        is_user_delegated_admin = len(user_delegated_admin_privilege) != 0
        if is_user_delegated_admin:
            user_access_grants.append(
                self.__construct_deldgated_admin_auth_grant(
                    user_delegated_admin_privilege)
            )

        return user_access_grants

    def __construct_fam_admin_auth_grant(self):
        fam_applications = self.application_repo.get_applications()
        fam_admin_auth_grant = FamAuthGrant(**{
            "auth_key": AdminRoleAuthGroup.FAM_ADMIN,
            "grants": list(map(
                lambda fam_application: FamGrantDetail(**{
                    "application": FamApplicationDto(
                        **fam_application.__dict__
                    )
                }), fam_applications))
        })
        return fam_admin_auth_grant

    def __construct_app_admin_auth_grant(
        self,
        granted_applications: List[FamApplication]
    ):
        app_admin_auth_grant = FamAuthGrant(**{
            "auth_key": AdminRoleAuthGroup.APP_ADMIN,
            "grants": list(map(
                lambda fam_application: FamGrantDetail(**{
                    "application": FamApplicationDto(
                        **fam_application.__dict__
                    ),
                    "roles": list(map(
                        lambda role: FamRoleDto(**role.__dict__),
                        self.role_repo.get_base_roles_by_app_id(
                            fam_application.application_id
                        )
                    ))
                }), granted_applications))
        })
        return app_admin_auth_grant

    def __construct_deldgated_admin_auth_grant(
        self,
        granted_roles: List[FamRole]
    ):
        delegated_admin_grants_details = []
        app_grouped_granted_roles = \
            itertools.groupby(
                granted_roles,
                lambda x: x.application_id)
        for _key, group in app_grouped_granted_roles:
            fam_roles = list(group)
            fam_application = fam_roles[0].application
            # TODO: group fam_roles for forest_client with the same parent_role_id
            delegated_admin_grants_details.append(FamGrantDetail(**{
                "application": FamApplicationDto(**fam_application.__dict__),
                "roles": list(map(
                    lambda role: FamRoleDto(**role.__dict__), fam_roles))
            }))

        delegated_admin_auth_grant = FamAuthGrant(**{
            "auth_key": AdminRoleAuthGroup.DELEGATED_ADMIN,
            "grants": delegated_admin_grants_details
        })

        return delegated_admin_auth_grant
