import logging

import pytest
from api.app.repositories.application_admin_repository import \
    ApplicationAdminRepository
from api.app.repositories.user_repository import UserRepository
from sqlalchemy.exc import IntegrityError
from tests.constants import (ERROR_VOLIATE_UNIQUE_CONSTRAINT,
                             TEST_ANOTHER_CREATER,
                             TEST_APPLICATION_ADMIN_APPLICATION_ID,
                             TEST_APPLICATION_ID_FAM,
                             TEST_APPLICATION_ID_FOM_DEV, TEST_CREATOR,
                             TEST_NEW_APPLICATION_ADMIN_USER_ID,
                             TEST_NEW_IDIR_USER)

LOGGER = logging.getLogger(__name__)


def test_create_application_admin_and_get(
    application_admin_repo: ApplicationAdminRepository,
):
    # create a new application admin
    new_application_admin = application_admin_repo.create_application_admin(
        TEST_APPLICATION_ADMIN_APPLICATION_ID,
        TEST_NEW_APPLICATION_ADMIN_USER_ID,
        TEST_CREATOR,
    )
    assert new_application_admin.application_id == TEST_APPLICATION_ADMIN_APPLICATION_ID
    assert new_application_admin.user_id == TEST_NEW_APPLICATION_ADMIN_USER_ID

    # get the new created application admin
    application_admin = application_admin_repo.get_application_admin_by_app_and_user_id(
        TEST_APPLICATION_ADMIN_APPLICATION_ID,
        TEST_NEW_APPLICATION_ADMIN_USER_ID,
    )
    assert new_application_admin.user_id == application_admin.user_id
    assert new_application_admin.application_id == application_admin.application_id
    assert (
        new_application_admin.application_admin_id
        == application_admin.application_admin_id
    )

    # create duplicate application admin
    with pytest.raises(IntegrityError) as e:
        application_admin_repo.create_application_admin(
            TEST_APPLICATION_ADMIN_APPLICATION_ID,
            TEST_NEW_APPLICATION_ADMIN_USER_ID,
            TEST_ANOTHER_CREATER,
        )
    assert str(e.value).find(ERROR_VOLIATE_UNIQUE_CONSTRAINT) != -1


def test_get_application_admin_by_id(
    application_admin_repo: ApplicationAdminRepository,
):
    # create a new application admin
    new_application_admin = application_admin_repo.create_application_admin(
        TEST_APPLICATION_ADMIN_APPLICATION_ID,
        TEST_NEW_APPLICATION_ADMIN_USER_ID,
        TEST_CREATOR,
    )
    # get the new application admin by id
    application_admin = application_admin_repo.get_application_admin_by_id(
        new_application_admin.application_admin_id
    )
    assert (
        application_admin.application_admin_id
        == new_application_admin.application_admin_id
    )


def test_delete_application_admin(application_admin_repo: ApplicationAdminRepository):
    # create a new application admin
    new_application_admin = application_admin_repo.create_application_admin(
        TEST_APPLICATION_ADMIN_APPLICATION_ID,
        TEST_NEW_APPLICATION_ADMIN_USER_ID,
        TEST_CREATOR,
    )
    # verify the new application admin is created
    application_admin = application_admin_repo.get_application_admin_by_id(
        new_application_admin.application_admin_id
    )
    assert application_admin is not None

    # remove the application admin
    application_admin_repo.delete_application_admin(
        new_application_admin.application_admin_id
    )
    # verify the application admin cannot be found anymore
    application_admin = application_admin_repo.get_application_admin_by_id(
        new_application_admin.application_admin_id
    )
    assert application_admin is None


def test_get_user_app_admin_grants(
    application_admin_repo: ApplicationAdminRepository,
    user_repo: UserRepository
):
    # no existing user.
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert fam_user is None

    # prepare a new user
    user_repo.create_user(TEST_NEW_IDIR_USER)
    new_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert new_user.user_name == TEST_NEW_IDIR_USER.user_name
    assert new_user.user_type_code == TEST_NEW_IDIR_USER.user_type_code

    # add new_user as a new FAM admin
    new_fam_admin = application_admin_repo.create_application_admin(
        TEST_APPLICATION_ID_FAM,
        new_user.user_id,
        TEST_CREATOR,
    )
    assert new_fam_admin.application_id == TEST_APPLICATION_ID_FAM
    assert new_fam_admin.user_id == new_user.user_id

    # test get_user_app_admin_grants for FAM admin user "new_user".
    fam_admin_grants = application_admin_repo.get_user_app_admin_grants(
        new_user.user_id
    )

    # granted application for the user should be only for FAM.
    assert len(fam_admin_grants) == 1
    granted_app = fam_admin_grants[0]
    assert granted_app.application_id == TEST_APPLICATION_ID_FAM

    # add new_user as a new FOM_DEV admin
    new_app_admin = application_admin_repo.create_application_admin(
        TEST_APPLICATION_ID_FOM_DEV,
        new_user.user_id,
        TEST_CREATOR,
    )
    assert new_app_admin.application_id == TEST_APPLICATION_ID_FOM_DEV
    assert new_app_admin.user_id == new_user.user_id

    # test get_user_app_admin_grants for "new_user".
    app_admin_grants = application_admin_repo.get_user_app_admin_grants(
        new_user.user_id
    )

    # granted applications for the user should be for FAM and FOM_DEV.
    assert len(app_admin_grants) == 2
    granted_application_list = list(
        map(lambda x: x.application_id, app_admin_grants)
    )
    assert set(granted_application_list) == set(
        [TEST_APPLICATION_ID_FAM, TEST_APPLICATION_ID_FOM_DEV])

    # unassign FAM application admin from new_user
    application_admin_repo.delete_application_admin(
        new_fam_admin.application_admin_id
    )
    fam_admin = application_admin_repo.get_application_admin_by_id(
        new_fam_admin.application_admin_id
    )
    assert fam_admin is None

    # test get_user_app_admin_grants for "new_user".
    admin_grants = application_admin_repo.get_user_app_admin_grants(
        new_user.user_id
    )

    # granted application for the user should now be only for FOM_DEV.
    assert len(admin_grants) == 1
    granted_app = admin_grants[0]
    assert granted_app.application_id == TEST_APPLICATION_ID_FOM_DEV