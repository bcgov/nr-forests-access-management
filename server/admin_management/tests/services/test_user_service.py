import logging

from api.app.repositories.user_repository import UserRepository
from api.app.services.user_service import UserService
from tests.constants import (TEST_NEW_BCEID_USER, TEST_NEW_IDIR_USER,
                             TEST_USER_BUSINESS_GUID_BCEID)

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


# TODO: this is removed due to business_guid update is now part of
# update_user_properties_from_verified_target_user(). Add new tests instead.

# def test_update_user_business_guid(
#     user_service: UserService, user_repo: UserRepository
# ):
#     # create a business user
#     new_user = user_repo.create_user(TEST_NEW_BCEID_USER)
#     # verify new user is created
#     found_user = user_service.get_user_by_domain_and_name(
#         TEST_NEW_BCEID_USER.user_type_code, TEST_NEW_BCEID_USER.user_name
#     )
#     assert new_user.user_id == found_user.user_id

#     # test update business guid when no business guid stored
#     updated_user = user_service.update_user_business_guid(
#         found_user.user_id,
#         TEST_USER_BUSINESS_GUID_BCEID,
#         TEST_NEW_IDIR_USER.create_user,
#     )
#     assert updated_user.business_guid == TEST_USER_BUSINESS_GUID_BCEID
#     # verify the business_guid is updated
#     found_user = user_service.get_user_by_domain_and_name(
#         TEST_NEW_BCEID_USER.user_type_code, TEST_NEW_BCEID_USER.user_name
#     )
#     assert found_user.user_id == updated_user.user_id
#     assert found_user.business_guid == TEST_USER_BUSINESS_GUID_BCEID

#     # test update business guid when business guid mismatch
#     new_business_guid = "MOCKEDNEWBUSINESSGUID5D4ACA9FA90"
#     updated_user = user_service.update_user_business_guid(
#         found_user.user_id, new_business_guid, TEST_NEW_IDIR_USER.create_user
#     )
#     assert updated_user.business_guid == new_business_guid
#     # verify the business guid is updated
#     found_user = user_service.get_user_by_domain_and_name(
#         TEST_NEW_BCEID_USER.user_type_code, TEST_NEW_BCEID_USER.user_name
#     )
#     assert found_user.user_id == updated_user.user_id
#     assert found_user.business_guid == new_business_guid

#     # test business no need to be updated
#     updated_user = user_service.update_user_business_guid(
#         found_user.user_id, new_business_guid, TEST_NEW_IDIR_USER.create_user
#     )
#     assert updated_user.business_guid == new_business_guid
#     # verify the business guid is updated
#     found_user = user_service.get_user_by_domain_and_name(
#         TEST_NEW_BCEID_USER.user_type_code, TEST_NEW_BCEID_USER.user_name
#     )
#     assert found_user.user_id == updated_user.user_id
#     assert found_user.business_guid == new_business_guid
