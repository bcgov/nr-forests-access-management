import logging

from api.app.services.user_service import UserService
from tests.constants import TEST_NEW_IDIR_USER


LOGGER = logging.getLogger(__name__)


def test_find_or_create(user_service: UserService):
    # verify the new user not exists
    found_user = user_service.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert found_user is None
    initial_users_count = user_service.get_users()

    # give the new user
    new_user = user_service.find_or_create(
        TEST_NEW_IDIR_USER.user_type_code,
        TEST_NEW_IDIR_USER.user_name,
        TEST_NEW_IDIR_USER.create_user,
    )
    assert new_user.user_name == TEST_NEW_IDIR_USER.user_name
    assert new_user.user_type_code == TEST_NEW_IDIR_USER.user_type_code
    # verify new user got created
    found_user = user_service.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert new_user.user_id == found_user.user_id
    assert new_user.user_name == found_user.user_name
    assert new_user.user_type_code == found_user.user_type_code
    after_add_users_count = user_service.get_users()
    assert len(after_add_users_count) == len(initial_users_count) + 1

    # give the existing user
    user_service.find_or_create(
        TEST_NEW_IDIR_USER.user_type_code,
        TEST_NEW_IDIR_USER.user_name,
        TEST_NEW_IDIR_USER.create_user,
    )
    users = user_service.get_users()
    # verify no user created
    assert len(users) == len(after_add_users_count)
