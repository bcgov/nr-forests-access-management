import logging

import pytest
import tests.jwt_utils as jwt_utils
from api.app.repositories.user_repository import UserRepository
from sqlalchemy.exc import IntegrityError
from tests.constants import (ERROR_VOLIATE_UNIQUE_CONSTRAINT,
                             TEST_NEW_BCEID_USER, TEST_NEW_IDIR_USER,
                             TEST_NON_EXISTS_COGNITO_USER_ID)

LOGGER = logging.getLogger(__name__)


def test_get_user_by_domain_and_name(user_repo: UserRepository):
    # test not found
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert fam_user is None

    # create a new user and find it and verify found
    new_user = user_repo.create_user(TEST_NEW_IDIR_USER)
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_guid == fam_user.user_guid
    assert new_user.user_type_code == fam_user.user_type_code

    # get user with username lower case
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_guid == fam_user.user_guid
    assert new_user.user_type_code == fam_user.user_type_code


def test_get_user_by_domain_and_guid(user_repo: UserRepository):
    # test not found
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert fam_user is None

    # create a new user
    new_user = user_repo.create_user(TEST_NEW_IDIR_USER)
    # verify the user can be found by domain and guid
    fam_user = user_repo.get_user_by_domain_and_guid(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_guid
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_guid == fam_user.user_guid
    assert new_user.user_type_code == fam_user.user_type_code


def test_get_user_by_cognito_user_id(user_repo: UserRepository):
    # test not found
    fam_user = user_repo.get_user_by_cognito_user_id(TEST_NON_EXISTS_COGNITO_USER_ID)
    assert fam_user is None

    # test found
    fam_user = user_repo.get_user_by_cognito_user_id(jwt_utils.COGNITO_USERNAME)
    assert fam_user.cognito_user_id == jwt_utils.COGNITO_USERNAME


def test_get_users(user_repo: UserRepository):
    users = user_repo.get_users()
    assert users is not None
    users_count = len(users)

    user_repo.create_user(TEST_NEW_IDIR_USER)
    users = user_repo.get_users()
    assert len(users) == users_count + 1


def test_create_user(user_repo: UserRepository):
    new_user = user_repo.create_user(TEST_NEW_IDIR_USER)
    assert new_user.user_name == TEST_NEW_IDIR_USER.user_name
    assert new_user.user_guid == TEST_NEW_IDIR_USER.user_guid
    assert new_user.user_type_code == TEST_NEW_IDIR_USER.user_type_code
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_IDIR_USER.user_type_code, TEST_NEW_IDIR_USER.user_name
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code

    # test create duplicate user
    with pytest.raises(IntegrityError) as e:
        user_repo.create_user(TEST_NEW_IDIR_USER)
    assert str(e.value).find(ERROR_VOLIATE_UNIQUE_CONSTRAINT) != -1


def test_update(user_repo: UserRepository):
    # create new user
    new_user = user_repo.create_user(TEST_NEW_BCEID_USER)
    assert new_user.user_id is not None
    assert new_user.user_name == TEST_NEW_BCEID_USER.user_name
    assert new_user.user_guid == TEST_NEW_BCEID_USER.user_guid
    assert new_user.user_type_code == TEST_NEW_BCEID_USER.user_type_code
    assert new_user.create_user == TEST_NEW_BCEID_USER.create_user
    assert new_user.business_guid is None
    assert new_user.update_user is None
    assert new_user.update_date is not None

    different_requester = "OTHER_TESTER"
    # update same user on "business_guid" from None to some value.
    update_value = {"business_guid": "some_new_value"}
    update_count = user_repo.update(new_user.user_id, update_value, different_requester)
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_BCEID_USER.user_type_code, TEST_NEW_BCEID_USER.user_name
    )

    assert update_count == 1
    assert fam_user.business_guid == update_value["business_guid"]
    assert fam_user.update_user == different_requester
    assert fam_user.update_date is not None
