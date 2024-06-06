import logging

import api.app.schemas as schemas
from api.app.crud import crud_user
from sqlalchemy.orm import Session
from testspg.constants import (
    TEST_NEW_USER,
    TEST_NOT_EXIST_USER_TYPE,
    TEST_NEW_BCEID_USER,
)

LOGGER = logging.getLogger(__name__)
NEW_USERNAME = "NEW_USERNAME"
NEW_USER_REQUEST = schemas.FamUser(**TEST_NEW_USER)


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
        db_pg_session, TEST_NOT_EXIST_USER_TYPE, "user_name"
    )
    assert fam_user is None

    # create a new user and find it and verify found
    request_user = schemas.FamUser(**TEST_NEW_USER)
    new_user = crud_user.create_user(fam_user=request_user, db=db_pg_session)
    fam_user = crud_user.get_user_by_domain_and_name(
        db_pg_session, TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code

    # find user with username lower case
    fam_user = crud_user.get_user_by_domain_and_name(
        db_pg_session, TEST_NEW_USER["user_type_code"], "test_user"
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code


def test_get_user_by_domain_and_guid(db_pg_session: Session):
    # test not found
    fam_user = crud_user.get_user_by_domain_and_name(
        db_pg_session, TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
    )
    assert fam_user is None

    # create a new user
    new_user = crud_user.create_user(NEW_USER_REQUEST, db_pg_session)
    # verify the user can be found by domain and guid
    fam_user = crud_user.get_user_by_domain_and_guid(
        db_pg_session, TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_guid"]
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_guid == fam_user.user_guid
    assert new_user.user_type_code == fam_user.user_type_code


def test_create_user(db_pg_session: Session):
    # create user and verify can get that new user
    new_user = crud_user.create_user(fam_user=NEW_USER_REQUEST, db=db_pg_session)
    fam_user = crud_user.get_user_by_domain_and_name(
        db_pg_session, TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == fam_user.user_id
    assert new_user.user_name == fam_user.user_name
    assert new_user.user_type_code == fam_user.user_type_code


def test_find_or_create(db_pg_session: Session):
    # verify the new user not exists
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session, TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
    )
    assert found_user is None
    initial_users = crud_user.get_users(db_pg_session)
    # give the new user
    new_user = crud_user.find_or_create(
        db_pg_session,
        TEST_NEW_USER["user_type_code"],
        TEST_NEW_USER["user_name"],
        TEST_NEW_USER["user_guid"],
        TEST_NEW_USER["create_user"],
    )
    assert new_user.user_name == TEST_NEW_USER["user_name"]
    # verify new user got created
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session, TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
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
        TEST_NEW_USER["create_user"],
    )
    users = crud_user.get_users(db_pg_session)
    # verify no user created
    assert len(users) == len(after_add_users)


def test_update(db_pg_session: Session):
    # create new user
    created_user = crud_user.create_user(fam_user=NEW_USER_REQUEST, db=db_pg_session)
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
        db_pg_session, TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
    )

    assert update_count == 1
    assert fam_user.business_guid == update_value["business_guid"]
    assert fam_user.update_user == different_requester
    assert fam_user.update_date is not None


def test_update_user_name(db_pg_session: Session):
    # create a user
    new_user = crud_user.create_user(NEW_USER_REQUEST, db_pg_session)
    # verify new user is created
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session, TEST_NEW_USER["user_type_code"], TEST_NEW_USER["user_name"]
    )
    assert new_user.user_id == found_user.user_id

    # test update user name
    updated_user = crud_user.update_user_name(
        db_pg_session, found_user, NEW_USERNAME, TEST_NEW_USER["create_user"]
    )
    assert updated_user.user_name == NEW_USERNAME
    # verify the username is updated
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session, TEST_NEW_USER["user_type_code"], NEW_USERNAME
    )
    assert found_user.user_id == updated_user.user_id
    assert found_user.user_name == NEW_USERNAME

    # test user name no need to be updated
    updated_user = crud_user.update_user_name(
        db_pg_session, found_user, NEW_USERNAME.lower(), TEST_NEW_USER["create_user"]
    )
    assert updated_user.user_name == NEW_USERNAME
    # verify the username is not updated
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session, TEST_NEW_USER["user_type_code"], NEW_USERNAME
    )
    assert found_user.user_id == updated_user.user_id
    assert found_user.user_name == NEW_USERNAME


def test_update_user_business_guid(db_pg_session: Session):
    # create a business user
    new_user = crud_user.create_user(
        schemas.FamUser(**TEST_NEW_BCEID_USER), db_pg_session
    )
    # verify new user is created
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_BCEID_USER["user_type_code"],
        TEST_NEW_BCEID_USER["user_name"],
    )
    assert new_user.user_id == found_user.user_id

    # test update business guid when no business guid stored
    business_guid = "MOCKEDBUSINESSGUID5D4ACA9FA901EE"
    updated_user = crud_user.update_user_business_guid(
        db_pg_session,
        found_user.user_id,
        business_guid,
        TEST_NEW_USER["create_user"],
    )
    assert updated_user.business_guid == business_guid
    # verify the business_guid is updated
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_BCEID_USER["user_type_code"],
        TEST_NEW_BCEID_USER["user_name"],
    )
    assert found_user.user_id == updated_user.user_id
    assert found_user.business_guid == business_guid

    # test update business guid when business guid mismatch
    new_business_guid = "MOCKEDNEWBUSINESSGUID5D4ACA9FA90"
    updated_user = crud_user.update_user_business_guid(
        db_pg_session,
        found_user.user_id,
        new_business_guid,
        TEST_NEW_USER["create_user"],
    )
    assert updated_user.business_guid == new_business_guid
    # verify the business guid is updated
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_BCEID_USER["user_type_code"],
        TEST_NEW_BCEID_USER["user_name"],
    )
    assert found_user.user_id == updated_user.user_id
    assert found_user.business_guid == new_business_guid

    # test business no need to be updated
    updated_user = crud_user.update_user_business_guid(
        db_pg_session,
        found_user.user_id,
        new_business_guid,
        TEST_NEW_USER["create_user"],
    )
    assert updated_user.business_guid == new_business_guid
    # verify the business guid is updated
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        TEST_NEW_BCEID_USER["user_type_code"],
        TEST_NEW_BCEID_USER["user_name"],
    )
    assert found_user.user_id == updated_user.user_id
    assert found_user.business_guid == new_business_guid
