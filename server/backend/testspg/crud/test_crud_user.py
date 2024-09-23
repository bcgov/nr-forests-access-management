import logging

from api.app.schemas import FamUserSchema, TargetUserSchema
import pytest
from api.app.constants import CURRENT_TERMS_AND_CONDITIONS_VERSION, UserType
from api.app.crud import crud_user
from api.app.models.model import FamUserTermsConditions
from sqlalchemy import insert
from sqlalchemy.orm import Session
from testspg.constants import (
    TEST_CREATOR,
    TEST_NEW_BCEID_USER,
    TEST_NEW_USER,
    TEST_NOT_EXIST_USER_TYPE,
    USER_NAME_BCEID_LOAD_3_TEST,
    USER_NAME_BCEID_LOAD_3_TEST_CHILD_1,
)

LOGGER = logging.getLogger(__name__)
NEW_USERNAME = "NEW_USERNAME"
NEW_USER_REQUEST = FamUserSchema(**TEST_NEW_USER)


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
    request_user = FamUserSchema(**TEST_NEW_USER)
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


@pytest.mark.parametrize(
    "new_user_initial_config, update_properties",
    [
        (
            TEST_NEW_BCEID_USER,
            {
                "first_name": "test",
                "last_name": "bceid",
                "email": "becid_user@test.com",
                "business_guid": "test_business_guid",
            },
        ),
        (
            TEST_NEW_USER,
            {  # IDIR
                "first_name": "test",
                "last_name": "idir",
                "email": "idir_user@test.com",
                "business_guid": None,
            },
        ),
        (
            TEST_NEW_USER,
            {
                "first_name": None,
                "last_name": None,
                "email": None,
                "business_guid": None,
            },
        ),
    ],
)
def test_update_user_properties_from_verified_target_user(
    new_user_initial_config, update_properties, db_pg_session: Session
):
    # create a new user
    new_user = crud_user.create_user(
        FamUserSchema(**new_user_initial_config), db_pg_session
    )
    # verify new user is created with no additoinal properties set.
    found_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        new_user_initial_config["user_type_code"],
        new_user_initial_config["user_name"],
    )
    assert new_user.user_id == found_user.user_id
    assert new_user.first_name is None
    assert new_user.last_name is None
    assert new_user.email is None
    assert new_user.business_guid is None

    target_user = TargetUserSchema(**new_user_initial_config, **update_properties)
    updated_user = crud_user.update_user_properties_from_verified_target_user(
        db_pg_session, found_user.user_id, target_user, found_user.create_user
    )
    assert updated_user.user_id == found_user.user_id
    assert updated_user.first_name == update_properties.get("first_name")
    assert updated_user.last_name == update_properties.get("last_name")
    assert updated_user.email == update_properties.get("email")
    assert updated_user.business_guid == update_properties.get("business_guid")


def test_fetch_initial_requester_info_can_join_terms_conditions(db_pg_session: Session):
    bceid_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        UserType.BCEID,
        USER_NAME_BCEID_LOAD_3_TEST,
    )
    assert bceid_user is not None
    assert bceid_user.cognito_user_id is not None
    assert bceid_user.fam_user_terms_conditions is None

    # bceid_user accepts FamUserTermsConditions
    db_pg_session.execute(
        insert(FamUserTermsConditions),
        [
            {
                "user_id": bceid_user.user_id,
                "version": CURRENT_TERMS_AND_CONDITIONS_VERSION,
                "create_user": TEST_CREATOR,
            }
        ],
    )

    # this seems important, otherwise newly added attribute (T&C) won't
    # reflect on the user object in db session. Cannot use 'commit()',
    # or session won't be able to rollback after each test.
    db_pg_session.refresh(bceid_user)

    # when fetch bceid_user, T&C should be joined and return.
    fetched_user = crud_user.fetch_initial_requester_info(
        db_pg_session, bceid_user.cognito_user_id
    )
    assert fetched_user.user_id == bceid_user.user_id
    assert fetched_user.fam_user_terms_conditions is not None
    assert fetched_user.fam_user_terms_conditions.user_id == bceid_user.user_id


def test_fetch_initial_requester_info_can_join_its_delegated_admin_record(
    db_pg_session: Session,
):
    # the db user for backend/server has no permission to insert record
    # into `app_fam.fam_access_control_privileg` table. So use
    # "TEST-3-LOAD-CHILD-1" to test instead, it has existing flyway setup for
    # delegated admin.
    bceid_user = crud_user.get_user_by_domain_and_name(
        db_pg_session,
        UserType.BCEID,
        USER_NAME_BCEID_LOAD_3_TEST_CHILD_1,
    )
    assert bceid_user is not None
    assert bceid_user.cognito_user_id is not None

    fetched_user = crud_user.fetch_initial_requester_info(
        db_pg_session, bceid_user.cognito_user_id
    )
    assert fetched_user.user_id == bceid_user.user_id
    assert len(fetched_user.fam_access_control_privileges) > 0
    delegated_admin_record = fetched_user.fam_access_control_privileges[0]
    assert delegated_admin_record.user_id == bceid_user.user_id
