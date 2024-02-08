import logging

import pytest
from api.app.constants import AdminRoleAuthGroup
from api.app.repositories.application_repository import ApplicationRepository
from api.app.services.admin_user_access_service import AdminUserAccessService
from tests.constants import TEST_APPLICATION_ID_FAM, TEST_NEW_IDIR_USER

LOGGER = logging.getLogger(__name__)


def test_get_access_grants_user_with_fam_admin_privilege(
    setup_new_user,
    setup_new_app_admin,
    admin_user_access_service: AdminUserAccessService,
    application_repo: ApplicationRepository,
):
    new_user = setup_new_user(TEST_NEW_IDIR_USER.user_type_code,
                              TEST_NEW_IDIR_USER.user_name)
    new_fam_admin = setup_new_app_admin(new_user.user_id,
                                              TEST_APPLICATION_ID_FAM)
    assert new_fam_admin.user_id == new_user.user_id
    assert new_fam_admin.application_id == TEST_APPLICATION_ID_FAM

    user_privilege = admin_user_access_service.get_access_grants(new_user.user_id)
    assert len(user_privilege.access) == 1
    access = user_privilege.access[0]
    assert access.auth_key == AdminRoleAuthGroup.FAM_ADMIN
    assert access.grants[0].roles is None
    assert access.grants[0].application is not None

    fam_applications = application_repo.get_applications()
    application_list = list(map(lambda x: x.application_id, fam_applications))
    auth_grant_applications = list(map(lambda x: x.application.id, access.grants))
    assert len(auth_grant_applications) == len(application_list)
    assert set(auth_grant_applications) == set(application_list)

