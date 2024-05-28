import logging

from api.app.constants import AdminRoleAuthGroup, AppEnv, RoleType
from api.app.repositories.application_repository import ApplicationRepository
from api.app.repositories.role_repository import RoleRepository
from api.app.services.admin_user_access_service import AdminUserAccessService
from tests.constants import (
    TEST_APPLICATION_ID_FAM,
    TEST_APPLICATION_ID_FOM_DEV,
    TEST_APPLICATION_ID_FOM_TEST,
    TEST_FOM_DEV_REVIEWER_ROLE_ID,
    TEST_FOM_TEST_SUBMITTER_ROLE_ID,
    TEST_FOREST_CLIENT_NUMBER,
    TEST_FOREST_CLIENT_NUMBER_TWO,
    TEST_NEW_BCEID_USER,
    TEST_NEW_IDIR_USER,
)

LOGGER = logging.getLogger(__name__)

# Below tests are based on endpoint json sample output at confluence design:
# https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Delegated+Access+Administration+Design


def test_get_access_grants_user_with_fam_admin_privilege(
    setup_new_user,
    setup_new_app_admin,
    admin_user_access_service: AdminUserAccessService,
    application_repo: ApplicationRepository,
):
    # setup new IDIR user
    new_user = setup_new_user(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name, TEST_NEW_IDIR_USER.user_guid
    )

    # verify new_user initially does not have any privilege
    user_privilege = admin_user_access_service.get_access_grants(new_user.user_id)
    assert user_privilege.access == []

    # add new_user to FAM_ADMIN
    new_fam_admin = setup_new_app_admin(new_user.user_id, TEST_APPLICATION_ID_FAM)
    assert new_fam_admin.user_id == new_user.user_id
    assert new_fam_admin.application_id == TEST_APPLICATION_ID_FAM

    user_privilege = admin_user_access_service.get_access_grants(new_user.user_id)
    assert len(user_privilege.access) == 1
    access = user_privilege.access[0]
    assert access.auth_key == AdminRoleAuthGroup.FAM_ADMIN
    assert access.grants[0].roles is None
    assert access.grants[0].application is not None

    # FAM_ADMIN can administer all FAM applications
    fam_applications = application_repo.get_applications()
    application_list = list(map(lambda x: x.application_id, fam_applications))
    auth_grant_applications = list(map(lambda x: x.application.id, access.grants))
    assert len(auth_grant_applications) == len(application_list)
    assert set(auth_grant_applications) == set(application_list)


def test_get_access_grants_user_with_app_admin_privilege(
    setup_new_user,
    setup_new_app_admin,
    admin_user_access_service: AdminUserAccessService,
    role_repo: RoleRepository,
):
    # setup new IDIR user
    new_user = setup_new_user(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name, TEST_NEW_IDIR_USER.user_guid
    )

    # verify new_user initially does not have any privilege
    user_privilege = admin_user_access_service.get_access_grants(new_user.user_id)
    assert user_privilege.access == []

    # add new_user to FOM_DEV (APP) admin
    new_fom_dev_admin = setup_new_app_admin(
        new_user.user_id, TEST_APPLICATION_ID_FOM_DEV
    )
    assert new_fom_dev_admin.user_id == new_user.user_id
    assert new_fom_dev_admin.application_id == TEST_APPLICATION_ID_FOM_DEV

    user_privilege = admin_user_access_service.get_access_grants(new_user.user_id)
    assert len(user_privilege.access) == 1

    access = user_privilege.access[0]
    assert access.auth_key == AdminRoleAuthGroup.APP_ADMIN
    assert len(access.grants) == 1

    grant = access.grants[0]
    assert grant.roles is not None
    assert grant.application is not None

    # verify user is granted for FOM DEV
    granted_application = grant.application
    assert granted_application.id == TEST_APPLICATION_ID_FOM_DEV
    assert granted_application.env == AppEnv.APP_ENV_TYPE_DEV

    # verify FOM DEV app admin can administer on specific roles
    granted_roles = grant.roles
    fom_base_roles = role_repo.get_base_roles_by_app_id(TEST_APPLICATION_ID_FOM_DEV)
    assert len(granted_roles) == len(fom_base_roles)
    role_list = list(map(lambda x: x.role_id, fom_base_roles))
    auth_grant_roles = list(map(lambda x: x.id, granted_roles))
    assert set(auth_grant_roles) == set(role_list)

    # add new_user to FOM_TEST admin (multiple APP_ADMIN)
    new_fom_test_admin = setup_new_app_admin(
        new_user.user_id, TEST_APPLICATION_ID_FOM_TEST
    )
    assert new_fom_test_admin.user_id == new_user.user_id
    assert new_fom_test_admin.application_id == TEST_APPLICATION_ID_FOM_TEST

    user_privilege = admin_user_access_service.get_access_grants(new_user.user_id)
    assert len(user_privilege.access) == 1

    access = user_privilege.access[0]
    assert access.auth_key == AdminRoleAuthGroup.APP_ADMIN
    assert len(access.grants) == 2

    # FOM DEV app admin privilege
    fom_dev_app_admin_grant = (
        list(
            filter(
                lambda x: x.application.id == TEST_APPLICATION_ID_FOM_DEV, access.grants
            )
        )
    )[0]
    fom_dev_base_roles = role_repo.get_base_roles_by_app_id(TEST_APPLICATION_ID_FOM_DEV)
    assert len(fom_dev_app_admin_grant.roles) == len(fom_dev_base_roles)
    fom_dev_base_role_list = list(map(lambda x: x.role_id, fom_dev_base_roles))
    dev_auth_grant_roles = list(map(lambda x: x.id, fom_dev_app_admin_grant.roles))
    assert set(dev_auth_grant_roles) == set(fom_dev_base_role_list)

    # FOM TEST app admin privilege
    fom_test_app_admin_grant = (
        list(
            filter(
                lambda x: x.application.id == TEST_APPLICATION_ID_FOM_TEST,
                access.grants,
            )
        )
    )[0]
    fom_test_base_roles = role_repo.get_base_roles_by_app_id(
        TEST_APPLICATION_ID_FOM_TEST
    )
    assert len(fom_test_app_admin_grant.roles) == len(fom_test_base_roles)
    fom_test_base_role_list = list(map(lambda x: x.role_id, fom_test_base_roles))
    test_auth_grant_roles = list(map(lambda x: x.id, fom_test_app_admin_grant.roles))
    assert set(test_auth_grant_roles) == set(fom_test_base_role_list)


def test_get_access_grants_user_with_delegated_admin_privilege(
    setup_new_user,
    setup_new_fom_delegated_admin,
    admin_user_access_service: AdminUserAccessService,
):
    # setup new BCEID user
    new_user = setup_new_user(
        TEST_NEW_BCEID_USER.user_type_code, TEST_NEW_BCEID_USER.user_name, TEST_NEW_IDIR_USER.user_guid
    )

    # verify BCEID new_user initially does not have any privilege
    user_privilege = admin_user_access_service.get_access_grants(new_user.user_id)
    assert user_privilege.access == []

    # assign new_user FOM_REVIEWER delegated admin to FOM DEV
    dga_user_roles = setup_new_fom_delegated_admin(
        new_user.user_id, RoleType.ROLE_TYPE_CONCRETE, AppEnv.APP_ENV_TYPE_DEV
    )
    assert len(dga_user_roles) == 1
    dga_user_role = dga_user_roles[0]
    assert dga_user_role.user_id == new_user.user_id
    assert dga_user_role.user.user_type_code == TEST_NEW_BCEID_USER.user_type_code
    assert dga_user_role.role_id == TEST_FOM_DEV_REVIEWER_ROLE_ID

    user_privilege = admin_user_access_service.get_access_grants(new_user.user_id)
    assert len(user_privilege.access) == 1
    access = user_privilege.access[0]
    assert access.auth_key == AdminRoleAuthGroup.DELEGATED_ADMIN
    assert len(access.grants) == 1
    grant = access.grants[0]
    assert grant.application is not None
    assert grant.application.id == TEST_APPLICATION_ID_FOM_DEV
    assert grant.application.env == AppEnv.APP_ENV_TYPE_DEV
    assert len(grant.roles) == 1
    assert grant.roles[0].id == TEST_FOM_DEV_REVIEWER_ROLE_ID
    assert grant.roles[0].type_code == RoleType.ROLE_TYPE_CONCRETE

    # assign new_user FOM_SUBMITTER delegated admin role to FOM_TEST
    dga_submitter_forest_clients = [
        TEST_FOREST_CLIENT_NUMBER,
        TEST_FOREST_CLIENT_NUMBER_TWO,
    ]
    dga_user_roles = setup_new_fom_delegated_admin(
        new_user.user_id,
        RoleType.ROLE_TYPE_ABSTRACT,
        AppEnv.APP_ENV_TYPE_TEST,
        dga_submitter_forest_clients,
    )
    assert len(dga_user_roles) == 2
    for dga_user_role in dga_user_roles:
        assert dga_user_role.user_id == new_user.user_id
        assert dga_user_role.user.user_type_code == TEST_NEW_BCEID_USER.user_type_code
        assert (
            dga_user_role.role.parent_role_id == TEST_FOM_TEST_SUBMITTER_ROLE_ID
        )  # TEST env

    user_privilege = admin_user_access_service.get_access_grants(new_user.user_id)
    access = user_privilege.access[0]
    assert access.auth_key == AdminRoleAuthGroup.DELEGATED_ADMIN
    assert len(access.grants) == 2  # DEV and TEST grants
    fom_dev_grant_list = list(
        filter(lambda x: x.application.id == TEST_APPLICATION_ID_FOM_DEV, access.grants)
    )
    assert len(fom_dev_grant_list) == 1

    fom_test_grant_list = list(
        filter(
            lambda x: x.application.id == TEST_APPLICATION_ID_FOM_TEST, access.grants
        )
    )
    assert len(fom_test_grant_list) == 1
    fom_test_grant = fom_test_grant_list[0]
    assert fom_test_grant.application is not None
    assert fom_test_grant.application.id == TEST_APPLICATION_ID_FOM_TEST
    assert fom_test_grant.application.env == AppEnv.APP_ENV_TYPE_TEST
    assert len(grant.roles) == 1  # FOM_SUBMITTER role with forest_cliet numbers
    fom_test_granted_role = fom_test_grant.roles[0]
    assert fom_test_granted_role.id == TEST_FOM_TEST_SUBMITTER_ROLE_ID
    assert fom_test_granted_role.type_code == RoleType.ROLE_TYPE_ABSTRACT
    assert len(fom_test_granted_role.forest_clients) == 2
    assert set(fom_test_granted_role.forest_clients) == set(
        dga_submitter_forest_clients
    )
