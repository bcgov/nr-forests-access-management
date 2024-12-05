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
from api.app.schemas.schemas import (AdminUserAccessResponse,
                                     FamApplicationDto, FamAuthGrantDto,
                                     FamGrantDetailDto, FamRoleDto)
from api.app.utils import utils
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class AdminUserAccessService:
    def __init__(self, db: Session):
        self.application_admin_repo = ApplicationAdminRepository(db)
        self.access_control_privilege_repo = AccessControlPrivilegeRepository(db)
        self.application_repo = ApplicationRepository(db)
        self.role_repo = RoleRepository(db)

    def get_access_grants(self, user_id: int) -> AdminUserAccessResponse:
        """
        Find out access privilege granted for the user
        (FAM_ADMIN, APP_ADMIN, DELEGATED_ADMIN).

        :param user_id: primary id that is associated with the user.
        :return: List of admin access privilege for the user for what
                 applications/roles(scoped) the user can grant or None.
        """
        # FamApplication(s) granted for Admin user (FAM and others).
        user_admin_privilege = self.application_admin_repo \
            .get_user_app_admin_grants(user_id)

        # FamApplication(s) granted for APP_ADMIN (apps filtered out FAM)
        user_apps_admin_privilege = [
            granted_app for granted_app in user_admin_privilege
            if granted_app.application_name != APPLICATION_FAM
        ]

        # FamRole(s) granted for user as DELEGATED_ADMIN
        user_delegated_admin_privilege = self.access_control_privilege_repo \
            .get_user_delegated_admin_grants(user_id)

        user_access_grants: List[FamAuthGrantDto] = []
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

        # final response constructed for list of access grants.
        admin_user_access_response = AdminUserAccessResponse(**{
            "access": user_access_grants
        })

        return admin_user_access_response

    # -- Private methods

    def __construct_fam_admin_auth_grant(self):
        """
        Constract (auth_key = FAM_ADMIN) access grants.
        """
        fam_applications = self.application_repo.get_applications()
        fam_admin_auth_grant = FamAuthGrantDto(**{
            "auth_key": AdminRoleAuthGroup.FAM_ADMIN,
            "grants": self.__preprocess_grant_details(list(map(
                lambda fam_application: FamGrantDetailDto(**{
                    "application": FamApplicationDto(
                        **fam_application.__dict__
                    )
                }), fam_applications)))
        })

        return fam_admin_auth_grant

    def __construct_app_admin_auth_grant(
        self,
        granted_applications: List[FamApplication]
    ):
        """
        Constract (auth_key = APP_ADMIN) access grants.
        """
        app_admin_auth_grant = FamAuthGrantDto(**{
            "auth_key": AdminRoleAuthGroup.APP_ADMIN,
            "grants": self.__preprocess_grant_details(list(map(
                lambda fam_application: FamGrantDetailDto(**{
                    "application": FamApplicationDto(
                        **fam_application.__dict__
                    ),
                    "roles": list(map(
                        lambda role: FamRoleDto(**role.__dict__),
                        self.role_repo.get_base_roles_by_app_id(
                            fam_application.application_id
                        )
                    ))
                }), granted_applications)))
        })

        return app_admin_auth_grant

    def __construct_deldgated_admin_auth_grant(
        self,
        granted_roles: List[FamRole]
    ):
        """
        Constract (auth_key = DELEGATED_ADMIN) access grants.
        """
        delegated_admin_grants_details = []

        # The return type structure is (itertools._grouper object).
        # However, it is similar like a list of grouped roles in iterator,
        # like below with "list(group)" for each iteraction:
        # 1 iteration: [(application_id=2, FamRole(role_id=1)), (application_id=2, FamRole(role_id=2))]
        # 2 iteration: [(application_id=3, FamRole(role_id=5)), (application_id=3, FamRole(role_id=6))]
        app_grouped_granted_roles = \
            itertools.groupby(granted_roles, (
                lambda fam_role: fam_role.application_id))

        for _key, group in app_grouped_granted_roles:
            fam_roles = list(group)
            fam_application = fam_roles[0].application

            roles_details: List[FamGrantDetailDto] = []
            parent_id_grouped_roles = itertools.groupby(fam_roles, (
                lambda fam_role: fam_role.parent_role_id))
            for key, group in parent_id_grouped_roles:
                if (key is None):  # Abstract role case (role without parent_role_id).
                    roles_details.extend(list(
                        map(lambda fam_role: FamRoleDto(**fam_role.__dict__),
                            group)))

                else:  # Concrete role case.
                    child_roles_group = list(group)
                    parent_role = child_roles_group[0].parent_role

                    # role_dto is an dto for abstract(parent) role with child
                    # roles of forest_clients associated.
                    role_dto = FamRoleDto(**parent_role.__dict__)
                    forest_client_numbers = list(
                        map(lambda fam_role: fam_role.forest_client_relation.forest_client_number,
                            child_roles_group))
                    role_dto.forest_clients = forest_client_numbers
                    roles_details.append(role_dto)

            delegated_admin_grants_details.append(FamGrantDetailDto(**{
                "application": FamApplicationDto(**fam_application.__dict__),
                "roles": roles_details
            }))

        delegated_admin_auth_grant = FamAuthGrantDto(**{
            "auth_key": AdminRoleAuthGroup.DELEGATED_ADMIN,
            "grants": self.__preprocess_grant_details(
                delegated_admin_grants_details)
        })

        return delegated_admin_auth_grant

    def __preprocess_grant_details(self, grant_details: List[FamGrantDetailDto]):
        """
        Some data might need to be processed before return; such as
        "application.name" currently in db has "_DEV","_TEST","_PROD" suffix.
        """
        for grant_detail in grant_details:
            grant_detail.application = self.__remove_app_env_suffix(
                grant_detail.application)

        return grant_details

    # remove suffix from application.name (e.g., FOM_DEV to FOM)
    def __remove_app_env_suffix(self, application: FamApplicationDto):
        application.name = utils.remove_app_env_suffix(application.name)
        return application
