import logging

from api.app.repositories.application_admin_repository import ApplicationAdminRepository

from tests.constants import (
    TEST_APPLICATION_ADMIN_ID,
    TEST_NEW_APPLICATION_ADMIN_USER_ID,
    TEST_CREATOR,
)


LOGGER = logging.getLogger(__name__)


def test_create_application_admin_and_get(
    application_admin_repo: ApplicationAdminRepository,
):
    # create a new application admin
    new_application_admin = application_admin_repo.create_application_admin(
        TEST_APPLICATION_ADMIN_ID,
        TEST_NEW_APPLICATION_ADMIN_USER_ID,
        TEST_CREATOR,
    )
    assert new_application_admin.application_id == TEST_APPLICATION_ADMIN_ID
    assert new_application_admin.user_id == TEST_NEW_APPLICATION_ADMIN_USER_ID

    # get the new created application admin
    application_admin = application_admin_repo.get_application_admin_by_app_and_user_id(
        TEST_APPLICATION_ADMIN_ID,
        TEST_NEW_APPLICATION_ADMIN_USER_ID,
    )
    assert new_application_admin.user_id == application_admin.user_id
    assert new_application_admin.application_id == application_admin.application_id
    assert (
        new_application_admin.application_admin_id
        == application_admin.application_admin_id
    )


def test_get_application_admin_by_application_id(
    application_admin_repo: ApplicationAdminRepository,
):
    # find application admin and get count
    application_admins = application_admin_repo.get_application_admin_by_application_id(
        TEST_APPLICATION_ADMIN_ID
    )
    assert application_admins is not None
    application_admin_count = len(application_admins)

    # create a new application admin
    new_application_admin = application_admin_repo.create_application_admin(
        TEST_APPLICATION_ADMIN_ID,
        TEST_NEW_APPLICATION_ADMIN_USER_ID,
        TEST_CREATOR,
    )
    assert new_application_admin.application_id == TEST_APPLICATION_ADMIN_ID
    # get the new application admin by application id
    application_admins = application_admin_repo.get_application_admin_by_application_id(
        TEST_APPLICATION_ADMIN_ID
    )
    assert application_admins is not None
    assert len(application_admins) == application_admin_count + 1


def test_get_application_admin_by_id(
    application_admin_repo: ApplicationAdminRepository,
):
    # create a new application admin
    new_application_admin = application_admin_repo.create_application_admin(
        TEST_APPLICATION_ADMIN_ID,
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
        TEST_APPLICATION_ADMIN_ID,
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
