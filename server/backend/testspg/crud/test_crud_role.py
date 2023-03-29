from sqlalchemy.orm import Session
import logging
import pytest
from sqlalchemy.exc import IntegrityError
from api.app.crud import crud_role, crud_user_role, crud_forest_client
import api.app.schemas as schemas
import api.app.constants as constants
from testspg.constants import TEST_NOT_EXIST_ROLE_ID, \
    TEST_FOM_DEV_REVIEWER_ROLE_ID, \
    TEST_FOM_DEV_SUBMITTER_ROLE_ID, \
    TEST_FOM_DEV_APPLICATION_ID, \
    TEST_CREATOR, \
    TEST_FOM_TEST_APPLICATION_ID, \
    TEST_NOT_EXIST_APPLICATION_ID

LOGGER = logging.getLogger(__name__)

TEST_NEW_ROLE = "TEST_READ"
TEST_NEW_ROLE_TWO = "TEST_WRITE"
TEST_FOREST_CLIENT_NUMBER = "00000002"
TEST_FOREST_CLIENT_NUMBER_TWO = "00000003"


def test_get_roles(dbPgSession: Session):
    roles = crud_role.get_roles(dbPgSession)
    assert len(roles) > 1


def test_get_role(dbPgSession: Session):
    # get non exists role
    found_role = crud_role.get_role(dbPgSession, TEST_NOT_EXIST_ROLE_ID)
    assert found_role is None

    # get concreate role
    found_role = crud_role.get_role(dbPgSession, TEST_FOM_DEV_REVIEWER_ROLE_ID)
    assert found_role.role_id == TEST_FOM_DEV_REVIEWER_ROLE_ID
    assert found_role.role_name == "FOM_REVIEWER"
    assert found_role.application_id == TEST_FOM_DEV_APPLICATION_ID

    # get abstract role
    found_role = crud_role.get_role(dbPgSession, TEST_FOM_DEV_SUBMITTER_ROLE_ID)
    assert found_role.role_id == TEST_FOM_DEV_SUBMITTER_ROLE_ID
    assert found_role.role_name == "FOM_SUBMITTER"
    assert found_role.application_id == TEST_FOM_DEV_APPLICATION_ID


def test_create_role(dbPgSession: Session):
    new_role = crud_role.create_role(
        schemas.FamRoleCreate(
            **{
                "application_id": TEST_FOM_DEV_APPLICATION_ID,
                "role_name": TEST_NEW_ROLE,
                "role_purpose": "test role",
                "create_user": TEST_CREATOR,
                "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
            }
        ),
        dbPgSession,
    )
    assert new_role.role_name == TEST_NEW_ROLE

    # verify role created
    found_role = crud_role.get_role(dbPgSession, new_role.role_id)
    assert found_role.role_id == new_role.role_id
    assert found_role.role_name == TEST_NEW_ROLE
    assert found_role.application_id == TEST_FOM_DEV_APPLICATION_ID
    assert found_role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE


def test_create_role_duplicate(dbPgSession: Session):
    # can not create the role with same role name, even with a different creator
    with pytest.raises(IntegrityError) as e:
        crud_role.create_role(
            schemas.FamRoleCreate(
                **{
                    "application_id": TEST_FOM_DEV_APPLICATION_ID,
                    "role_name": TEST_NEW_ROLE,
                    "role_purpose": "test role",
                    "create_user": "ANOTHER_CREATOR",
                    "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
                }
            ),
            dbPgSession,
        )
    assert str(e.value).find("duplicate key value violates unique constraint") != -1
    dbPgSession.rollback()


def test_create_role_child_role_with_forest_client(dbPgSession: Session):
    new_child_role = crud_role.create_role(
        schemas.FamRoleCreate(
            **{
                "parent_role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
                "application_id": TEST_FOM_DEV_APPLICATION_ID,
                "forest_client_number": TEST_FOREST_CLIENT_NUMBER,
                "role_name": "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER,
                "role_purpose": crud_user_role.construct_forest_client_role_purpose(
                    "PARENT_ROLE purpose",
                    TEST_FOREST_CLIENT_NUMBER
                ),
                "create_user": TEST_CREATOR,
                "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
            }
        ),
        dbPgSession,
    )
    assert new_child_role.role_name == "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER

    # verify role created
    found_role = crud_role.get_role(dbPgSession, new_child_role.role_id)
    assert found_role.role_id == new_child_role.role_id
    assert found_role.role_name == "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER
    assert found_role.application_id == TEST_FOM_DEV_APPLICATION_ID
    assert found_role.parent_role_id == TEST_FOM_DEV_SUBMITTER_ROLE_ID
    assert found_role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE

    # make sure that a forest client record exists in the database
    forest_client_from_db = crud_forest_client.get_forest_client(
        db=dbPgSession, forest_client_number=TEST_FOREST_CLIENT_NUMBER)
    assert (
        forest_client_from_db.forest_client_number ==
        TEST_FOREST_CLIENT_NUMBER
    )


def test_create_role_child_role_with_invalid_parent(dbPgSession: Session):
    with pytest.raises(IntegrityError) as e:
        crud_role.create_role(
            schemas.FamRoleCreate(
                **{
                    "parent_role_id": TEST_NOT_EXIST_ROLE_ID,
                    "application_id": TEST_FOM_DEV_APPLICATION_ID,
                    "forest_client_number": TEST_FOREST_CLIENT_NUMBER_TWO,
                    "role_name": "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER_TWO,
                    "role_purpose": crud_user_role.construct_forest_client_role_purpose(
                        "PARENT_ROLE purpose",
                        TEST_FOREST_CLIENT_NUMBER_TWO
                    ),
                    "create_user": TEST_CREATOR,
                    "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
                }
            ),
            dbPgSession,
        )
    assert str(e.value).find("violates foreign key constraint") != -1
    dbPgSession.rollback()


def test_create_role_same_role_for_different_application(dbPgSession: Session):
    first_new_role = crud_role.create_role(
        schemas.FamRoleCreate(
            **{
                "application_id": TEST_FOM_DEV_APPLICATION_ID,
                "role_name": TEST_NEW_ROLE_TWO,
                "role_purpose": "test role",
                "create_user": TEST_CREATOR,
                "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
            }
        ),
        dbPgSession,
    )
    assert first_new_role.role_name == TEST_NEW_ROLE_TWO

    # verify first role created
    found_role = crud_role.get_role(dbPgSession, first_new_role.role_id)
    assert found_role.role_id == first_new_role.role_id
    assert found_role.role_name == TEST_NEW_ROLE_TWO
    assert found_role.application_id == TEST_FOM_DEV_APPLICATION_ID
    assert found_role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE

    second_new_role = crud_role.create_role(
        schemas.FamRoleCreate(
            **{
                "application_id": TEST_FOM_TEST_APPLICATION_ID,
                "role_name": TEST_NEW_ROLE_TWO,
                "role_purpose": "test role",
                "create_user": TEST_CREATOR,
                "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
            }
        ),
        dbPgSession,
    )
    assert second_new_role.role_name == TEST_NEW_ROLE_TWO

    # verify second role created
    found_role = crud_role.get_role(dbPgSession, first_new_role.role_id)
    assert second_new_role.role_id == second_new_role.role_id
    assert second_new_role.role_name == TEST_NEW_ROLE_TWO
    assert second_new_role.application_id == TEST_FOM_TEST_APPLICATION_ID
    assert second_new_role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE

    # verify two roles are for different application
    assert second_new_role.role_id != first_new_role.role_id
    assert second_new_role.application_id != first_new_role.application_id
    assert second_new_role.role_name == first_new_role.role_name


def test_get_role_by_role_name_and_app_id(dbPgSession: Session):
    # get with non existing role name
    found_role = crud_role.get_role_by_role_name_and_app_id(
        dbPgSession,
        "TEST_NON_ROLE",
        TEST_FOM_DEV_APPLICATION_ID
    )
    assert found_role is None

    # get with non existing application id
    found_role = crud_role.get_role_by_role_name_and_app_id(
        dbPgSession,
        "FOM_REVIEWER",
        TEST_NOT_EXIST_APPLICATION_ID
    )
    assert found_role is None

    # get with role not in application
    found_role = crud_role.get_role_by_role_name_and_app_id(
        dbPgSession,
        "FOM_REVIEWER",
        1  # FAM APPLICATION ID
    )
    assert found_role is None

    # get existing role
    found_role = crud_role.get_role_by_role_name_and_app_id(
        dbPgSession,
        "FOM_REVIEWER",
        TEST_FOM_DEV_APPLICATION_ID
    )
    assert found_role.role_name == "FOM_REVIEWER"

