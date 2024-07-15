import logging

import pytest

from api.app.repositories.user_repository import UserRepository
from api.app.schemas import TargetUser
from api.app.services.user_service import UserService
from tests.constants import TEST_NEW_BCEID_USER, TEST_NEW_IDIR_USER

LOGGER = logging.getLogger(__name__)
NEW_USERNAME = "NEW_USERNAME"


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
        TEST_NEW_IDIR_USER.user_guid,
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
        TEST_NEW_IDIR_USER.user_guid,
        TEST_NEW_IDIR_USER.create_user,
    )
    users = user_service.get_users()
    # verify no user created
    assert len(users) == len(after_add_users_count)

    # give the existing user with a new username need to be updated
    updated_user = user_service.find_or_create(
        TEST_NEW_IDIR_USER.user_type_code,
        NEW_USERNAME,
        TEST_NEW_IDIR_USER.user_guid,
        TEST_NEW_IDIR_USER.create_user,
    )
    users = user_service.get_users()
    # verify no user created
    assert len(users) == len(after_add_users_count)
    # verify username is updated
    assert updated_user.user_name == NEW_USERNAME


def test_update_user_name(user_service: UserService, user_repo: UserRepository):
    # create a user
    new_user = user_repo.create_user(TEST_NEW_IDIR_USER)
    # verify new user is created
    found_user = user_service.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert new_user.user_id == found_user.user_id

    # test update user name
    updated_user = user_service.update_user_name(
        found_user, NEW_USERNAME, TEST_NEW_IDIR_USER.create_user
    )
    assert updated_user.user_name == NEW_USERNAME
    # verify the username is updated
    found_user = user_service.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, NEW_USERNAME
    )
    assert found_user.user_id == updated_user.user_id
    assert found_user.user_name == NEW_USERNAME

    # test user name no need to be updated
    updated_user = user_service.update_user_name(
        found_user, NEW_USERNAME.lower(), TEST_NEW_IDIR_USER.create_user
    )
    assert updated_user.user_name == NEW_USERNAME
    # verify the username is not updated
    found_user = user_service.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, NEW_USERNAME
    )
    assert found_user.user_id == updated_user.user_id
    assert found_user.user_name == NEW_USERNAME


@pytest.mark.parametrize(
    "new_user_initial_config, update_properties",
    [
        (TEST_NEW_BCEID_USER, {
            "first_name": "test", "last_name": "bceid", "email": "becid_user@test.com", "business_guid": "test_business_guid"
        }),
        (TEST_NEW_IDIR_USER, {  # IDIR
            "first_name": "test", "last_name": "idir", "email": "idir_user@test.com", "business_guid": None
        }),
        (TEST_NEW_IDIR_USER, {
            "first_name": None, "last_name": None, "email": None, "business_guid": None
        })
    ]
)
def test_update_user_properties_from_verified_target_user(
    new_user_initial_config,
    update_properties,
    user_service: UserService,
    user_repo: UserRepository
):
    # create a new user
    new_user = user_repo.create_user(new_user_initial_config)
    # verify new user is created with no additoinal properties set.
    found_user = user_service.get_user_by_domain_and_name(
        new_user_initial_config.user_type_code,
        new_user_initial_config.user_name
    )
    assert new_user.user_id == found_user.user_id
    assert new_user.first_name is None
    assert new_user.last_name is None
    assert new_user.email is None
    assert new_user.business_guid is None

    target_user = TargetUser(
        **new_user_initial_config.__dict__,
        **update_properties
    )
    updated_user = user_service.update_user_properties_from_verified_target_user(
        found_user.user_id,
        target_user,
        found_user.create_user
    )
    assert updated_user.user_id == found_user.user_id
    assert updated_user.first_name == update_properties.get("first_name")
    assert updated_user.last_name == update_properties.get("last_name")
    assert updated_user.email == update_properties.get("email")
    assert updated_user.business_guid == update_properties.get("business_guid")
