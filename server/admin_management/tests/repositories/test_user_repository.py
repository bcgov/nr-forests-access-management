import logging
import pytest
from sqlalchemy.exc import IntegrityError

import api.app.schemas as schemas
from api.app.repositories.user_repository import UserRepository

from tests.constants import (
    TEST_NEW_USER,
    TEST_NON_EXISTS_COGNITO_USER_ID,
)
import tests.jwt_utils as jwt_utils


LOGGER = logging.getLogger(__name__)


def test_get_user_by_domain_and_name(user_repo: UserRepository):
    # test not found
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
    )
    assert fam_user is None

    # create a new user and find it and verify found
    request_user = schemas.FamUser(**TEST_NEW_USER)
    new_user = user_repo.create_user(request_user)
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code

    # get user with username lower case
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_USER["user_type_code"], "test_user"
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
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

    request_user = schemas.FamUser(**TEST_NEW_USER)
    user_repo.create_user(request_user)
    users = user_repo.get_users()
    assert len(users) == users_count + 1


def test_create_user(user_repo: UserRepository):
    request_user = schemas.FamUser(**TEST_NEW_USER)
    new_user = user_repo.create_user(request_user)
    assert new_user.user_name == TEST_NEW_USER.get("user_name")
    assert new_user.user_type_code == TEST_NEW_USER.get("user_type_code")
    fam_user = user_repo.get_user_by_domain_and_name(
        TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code

    # test create duplicate user
    with pytest.raises(IntegrityError) as e:
        user_repo.create_user(request_user)
    assert (
        str(e.value).find('duplicate key value violates unique constraint "fam_usr_uk"')
        != -1
    )
