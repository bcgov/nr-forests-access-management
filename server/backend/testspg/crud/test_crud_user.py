import logging

import api.app.schemas as schemas
from api.app.crud import crud_user
from sqlalchemy.orm import Session
from testspg.constants import TEST_NEW_USER, TEST_NOT_EXIST_USER_TYPE

LOGGER = logging.getLogger(__name__)


def test_get_users(db_pg_session: Session):
    users = crud_user.get_users(db_pg_session)
    assert len(users) > 1


def test_get_user(db_pg_session: Session):
    # get non exists user id
    user = crud_user.get_user(db_pg_session, 0)
    assert user is None

    # get user
    user = crud_user.get_user(db_pg_session, 1)
    assert user is not None
    assert user.user_id == 1


def test_get_user_by_domain_and_name(db_pg_session: Session):
    # get with non exist user type and username
    fam_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NOT_EXIST_USER_TYPE,
        "user_name"
    )
    assert fam_user is None

    # create a new user and find it and verify found
    request_user = schemas.FamUser(**TEST_NEW_USER)
    new_user = crud_user.create_user(fam_user=request_user, db=db_pg_session)
    fam_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code

    # find user with username lower case
    fam_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_USER["user_type_code"],
        "test_user"
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code


def test_create_user(db_pg_session: Session):
    # create user and verify can get that new user
    request_user = schemas.FamUser(**TEST_NEW_USER)
    new_user = crud_user.create_user(fam_user=request_user, db=db_pg_session)
    fam_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code


def test_find_or_create(db_pg_session: Session):
    # verify the new user not exists
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert found_user is None
    initial_users = crud_user.get_users(db_pg_session)
    # give the new user
    new_user = crud_user.find_or_create(
        db_pg_session,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"],
        TEST_NEW_USER["user_guid"],
        TEST_NEW_USER["create_user"]
    )
    assert new_user.user_name == TEST_NEW_USER["user_name"]
    # verify new user got created
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )
    assert found_user is not None
    assert found_user.user_name == TEST_NEW_USER["user_name"]
    after_add_users = crud_user.get_users(db_pg_session)
    assert len(after_add_users) == len(initial_users) + 1

    # give the existing user
    crud_user.find_or_create(
        db_pg_session,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"],
        TEST_NEW_USER["user_guid"],
        TEST_NEW_USER["create_user"]
    )
    users = crud_user.get_users(db_pg_session)
    # verify no user created
    assert len(users) == len(after_add_users)


def test_update(db_pg_session: Session):
    # create new user
    new_user_request = schemas.FamUser(**TEST_NEW_USER)
    created_user = crud_user.create_user(fam_user=new_user_request, db=db_pg_session)
    assert created_user.user_id is not None
    assert created_user.user_name == created_user.user_name
    assert created_user.user_type_code == created_user.user_type_code
    assert created_user.create_user == TEST_NEW_USER.get("create_user")
    assert created_user.business_guid is None
    assert created_user.update_user is None
    assert created_user.update_date is None

    different_requester = "OTHER_TESTER"
    # update same user on "business_guid" from None to some value.
    update_value = {"business_guid": "some_new_value"}
    update_count = crud_user.update(
        db_pg_session, created_user.user_id, update_value, different_requester
    )
    fam_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"]
    )

    assert update_count == 1
    assert fam_user.business_guid == update_value["business_guid"]
    assert fam_user.update_user == different_requester
    assert fam_user.update_date is not None
