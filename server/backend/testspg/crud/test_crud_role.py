import copy
import logging

import api.app.constants as constants
import pytest
from api.app.crud import crud_forest_client, crud_role, crud_user_role
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from testspg.constants import (
    TEST_CREATOR,
    FOM_DEV_APPLICATION_ID,
    FOM_DEV_REVIEWER_ROLE_ID,
    FOM_DEV_SUBMITTER_ROLE_ID,
    FOM_TEST_APPLICATION_ID,
    NOT_EXIST_APPLICATION_ID,
    NOT_EXIST_ROLE_ID,
)
from api.app.schemas import FamRoleCreateSchema

LOGGER = logging.getLogger(__name__)

TEST_NEW_ROLE = "TEST_READ"
TEST_NEW_ROLE_TWO = "TEST_WRITE"
TEST_FOREST_CLIENT_NUMBER = "00000002"
TEST_FOREST_CLIENT_NUMBER_TWO = "00000003"
TEST_ROLE_PURPOSE = "test role"
TEST_ROLE_CREATE = {
    "application_id": FOM_DEV_APPLICATION_ID,
    "role_name": TEST_NEW_ROLE,
    "role_purpose": TEST_ROLE_PURPOSE,
    "create_user": TEST_CREATOR,
    "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
}


def test_get_role(db_pg_session: Session):
    # get non exists role
    found_role = crud_role.get_role(db_pg_session, NOT_EXIST_ROLE_ID)
    assert found_role is None

    # get concreate role
    found_role = crud_role.get_role(db_pg_session, FOM_DEV_REVIEWER_ROLE_ID)
    assert found_role.role_id == FOM_DEV_REVIEWER_ROLE_ID
    assert found_role.role_name == "FOM_REVIEWER"
    assert found_role.application_id == FOM_DEV_APPLICATION_ID

    # get abstract role
    found_role = crud_role.get_role(db_pg_session, FOM_DEV_SUBMITTER_ROLE_ID)
    assert found_role.role_id == FOM_DEV_SUBMITTER_ROLE_ID
    assert found_role.role_name == "FOM_SUBMITTER"
    assert found_role.application_id == FOM_DEV_APPLICATION_ID


def test_create_role(db_pg_session: Session):
    new_role = crud_role.create_role(
        FamRoleCreateSchema(**TEST_ROLE_CREATE),
        db_pg_session,
    )
    assert new_role.role_name == TEST_NEW_ROLE

    # verify role created
    found_role = crud_role.get_role(db_pg_session, new_role.role_id)
    assert found_role.role_id == new_role.role_id
    assert found_role.role_name == TEST_NEW_ROLE
    assert found_role.application_id == FOM_DEV_APPLICATION_ID
    assert found_role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE


def test_create_role_duplicate(db_pg_session: Session):
    # create a role ininitally
    new_role = crud_role.create_role(
        FamRoleCreateSchema(**TEST_ROLE_CREATE),
        db_pg_session,
    )
    assert new_role.role_name == TEST_NEW_ROLE

    # can not create the role with same role name, even with a different creator
    with pytest.raises(IntegrityError) as e:
        crud_role.create_role(
            FamRoleCreateSchema(
                **{
                    "application_id": TEST_ROLE_CREATE["application_id"],
                    "role_name": TEST_ROLE_CREATE["role_name"],
                    "role_purpose": TEST_ROLE_CREATE["role_purpose"],
                    "create_user": "ANOTHER_CREATOR",
                    "role_type_code": TEST_ROLE_CREATE["role_type_code"],
                }
            ),
            db_pg_session,
        )
    assert str(e.value).find("duplicate key value violates unique constraint") != -1


def test_create_role_child_role_with_forest_client(db_pg_session: Session):
    new_child_role = crud_role.create_role(
        FamRoleCreateSchema(
            **{
                "parent_role_id": FOM_DEV_SUBMITTER_ROLE_ID,
                "application_id": FOM_DEV_APPLICATION_ID,
                "forest_client_number": TEST_FOREST_CLIENT_NUMBER,
                "role_name": "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER,
                "role_purpose": crud_user_role.construct_forest_client_role_purpose(
                    "PARENT_ROLE purpose", TEST_FOREST_CLIENT_NUMBER
                ),
                "create_user": TEST_CREATOR,
                "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
            }
        ),
        db_pg_session,
    )
    assert new_child_role.role_name == "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER

    # verify role created
    found_role = crud_role.get_role(db_pg_session, new_child_role.role_id)
    assert found_role.role_id == new_child_role.role_id
    assert found_role.role_name == "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER
    assert found_role.application_id == FOM_DEV_APPLICATION_ID
    assert found_role.parent_role_id == FOM_DEV_SUBMITTER_ROLE_ID
    assert found_role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE

    # make sure that a forest client record exists in the database
    forest_client_from_db = crud_forest_client.get_forest_client(
        db=db_pg_session, forest_client_number=TEST_FOREST_CLIENT_NUMBER
    )
    assert forest_client_from_db.forest_client_number == TEST_FOREST_CLIENT_NUMBER


def test_create_role_child_role_with_invalid_parent(db_pg_session: Session):
    with pytest.raises(IntegrityError) as e:
        crud_role.create_role(
            FamRoleCreateSchema(
                **{
                    "parent_role_id": NOT_EXIST_ROLE_ID,
                    "application_id": FOM_DEV_APPLICATION_ID,
                    "forest_client_number": TEST_FOREST_CLIENT_NUMBER_TWO,
                    "role_name": "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER_TWO,
                    "role_purpose": crud_user_role.construct_forest_client_role_purpose(
                        "PARENT_ROLE purpose", TEST_FOREST_CLIENT_NUMBER_TWO
                    ),
                    "create_user": TEST_CREATOR,
                    "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
                }
            ),
            db_pg_session,
        )
    assert str(e.value).find("violates foreign key constraint") != -1


def test_create_role_same_role_for_different_application(db_pg_session: Session):
    copy_test_role_create = copy.deepcopy(TEST_ROLE_CREATE)
    copy_test_role_create["role_name"] = TEST_NEW_ROLE_TWO
    first_new_role = crud_role.create_role(
        FamRoleCreateSchema(**copy_test_role_create),
        db_pg_session,
    )
    assert first_new_role.role_name == TEST_NEW_ROLE_TWO

    # verify first role created
    found_role = crud_role.get_role(db_pg_session, first_new_role.role_id)
    assert found_role.role_id == first_new_role.role_id
    assert found_role.role_name == TEST_NEW_ROLE_TWO
    assert found_role.application_id == FOM_DEV_APPLICATION_ID
    assert found_role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE

    copy_test_role_create["application_id"] = FOM_TEST_APPLICATION_ID
    second_new_role = crud_role.create_role(
        FamRoleCreateSchema(**copy_test_role_create),
        db_pg_session,
    )
    assert second_new_role.role_name == TEST_NEW_ROLE_TWO

    # verify second role created
    found_role = crud_role.get_role(db_pg_session, second_new_role.role_id)
    assert found_role.role_id == second_new_role.role_id
    assert found_role.role_name == TEST_NEW_ROLE_TWO
    assert found_role.application_id == FOM_TEST_APPLICATION_ID
    assert found_role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE

    # verify two roles are for different application
    assert second_new_role.role_id != first_new_role.role_id
    assert second_new_role.application_id != first_new_role.application_id
    assert second_new_role.role_name == first_new_role.role_name


def test_get_role_by_role_name_and_app_id(db_pg_session: Session):
    # get with non existing role name
    found_role = crud_role.get_role_by_role_name_and_app_id(
        db_pg_session, "TEST_NON_ROLE", FOM_DEV_APPLICATION_ID
    )
    assert found_role is None

    # get with non existing application id
    found_role = crud_role.get_role_by_role_name_and_app_id(
        db_pg_session, "FOM_REVIEWER", NOT_EXIST_APPLICATION_ID
    )
    assert found_role is None

    # get with role not in application
    found_role = crud_role.get_role_by_role_name_and_app_id(
        db_pg_session, "FOM_REVIEWER", 1  # FAM APPLICATION ID
    )
    assert found_role is None

    # get existing role
    found_role = crud_role.get_role_by_role_name_and_app_id(
        db_pg_session, "FOM_REVIEWER", FOM_DEV_APPLICATION_ID
    )
    assert found_role.role_name == "FOM_REVIEWER"
