from sqlalchemy.orm import Session
import logging
import pytest
# from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound
from api.app.crud import crud_user
import api.app.schemas as schemas
from testspg.constants import TEST_NEW_USER, TEST_NOT_EXIST_USER_TYPE

LOGGER = logging.getLogger(__name__)


def test_get_users(dbPgSession: Session):
    users = crud_user.get_users(dbPgSession)
    assert len(users) > 1


def test_get_user(dbPgSession: Session):
    # get non exists user id
    user = crud_user.get_user(dbPgSession, 0)
    assert user is None

    # get user
    user = crud_user.get_user(dbPgSession, 1)
    assert user is not None
    assert user.user_id == 1


def test_get_user_by_domain_and_name(dbPgSession: Session):
    # get with non exist user type and username
    fam_user = crud_user.get_user_by_domain_and_name(
        dbPgSession,
        TEST_NOT_EXIST_USER_TYPE,
        "user_name"
    )
    assert fam_user is None

    # create a new user and find it and verify found
    request_user = schemas.FamUser(**TEST_NEW_USER)
    new_user = crud_user.create_user(fam_user=request_user, db=dbPgSession)
    fam_user = crud_user.get_user_by_domain_and_name(
        dbPgSession,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code

    # find user with username lower case
    fam_user = crud_user.get_user_by_domain_and_name(
        dbPgSession,
        TEST_NEW_USER["user_type_code"],
        "test_user"
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code

    # cleanup
    crud_user.delete_user(dbPgSession, new_user.user_id)


def test_create_user(dbPgSession: Session):
    # create user with non exist user type
    # todo: test error doesn't got catched correctly
    # copy_user = copy.deepcopy(TEST_NEW_USER)
    # copy_user["user_type_code"] = TEST_NOT_EXIST_USER_TYPE
    # request_user = schemas.FamUser(**copy_user)
    # with pytest.raises(ValidationError) as e:
    #     assert schemas.FamUserRoleAssignmentCreate(**request_user)
    # assert (
    #     str(e.value).find(
    #         "value is not a valid enumeration member; permitted: 'I', 'B'"
    #     )
    #     != -1
    # )

    # create user and verify can get that new user
    request_user = schemas.FamUser(**TEST_NEW_USER)
    new_user = crud_user.create_user(fam_user=request_user, db=dbPgSession)
    fam_user = crud_user.get_user_by_domain_and_name(
        dbPgSession,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code

    # cleanup
    crud_user.delete_user(dbPgSession, new_user.user_id)


def test_delete_user(dbPgSession: Session):
    # create a user
    request_user = schemas.FamUser(**TEST_NEW_USER)
    new_user = crud_user.create_user(fam_user=request_user, db=dbPgSession)

    # verify can find the new user
    fam_user = crud_user.get_user_by_domain_and_name(
        dbPgSession,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == fam_user.user_id

    # delete user
    crud_user.delete_user(dbPgSession, new_user.user_id)

    # verify can not find that user anymore
    fam_user = crud_user.get_user_by_domain_and_name(
        dbPgSession,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert fam_user is None

    # delete non exist user
    with pytest.raises(NoResultFound) as e:
        crud_user.delete_user(dbPgSession, new_user.user_id)
    assert str(e.value) == "No row was found when one was required"


def test_find_or_create(dbPgSession: Session):
    # verify the new user not exists
    found_user = crud_user.get_user_by_domain_and_name(
        dbPgSession,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert found_user is None
    initial_users = crud_user.get_users(dbPgSession)
    # give the new user
    new_user = crud_user.find_or_create(
        dbPgSession,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"],
        TEST_NEW_USER["create_user"]
    )
    assert new_user.user_name == TEST_NEW_USER["user_name"]
    # verify new user got created
    found_user = crud_user.get_user_by_domain_and_name(
        dbPgSession,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert found_user is not None
    assert found_user.user_name == TEST_NEW_USER["user_name"]
    after_add_users = crud_user.get_users(dbPgSession)
    assert len(after_add_users) == len(initial_users) + 1

    # give the existing user
    new_user = crud_user.find_or_create(
        dbPgSession,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"],
        TEST_NEW_USER["create_user"]
    )
    users = crud_user.get_users(dbPgSession)
    # verify no user created
    assert len(users) == len(after_add_users)

