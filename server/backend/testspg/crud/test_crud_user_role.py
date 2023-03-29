from sqlalchemy.orm import Session
import logging
import pytest
from fastapi import HTTPException
import copy
from api.app.crud import crud_user_role, crud_role
import api.app.schemas as schemas
from testspg.constants import TEST_FOM_DEV_REVIEWER_ROLE_ID, \
    TEST_FOM_DEV_SUBMITTER_ROLE_ID, \
    TEST_CREATOR, \
    TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE, \
    TEST_NOT_EXIST_ROLE_ID

LOGGER = logging.getLogger(__name__)

TEST_USER_ID = 1
TEST_FOREST_CLIENT_NUMBER = "00000001"


def test_create_user_role_with_role_not_exists(dbPgSession: Session):
    user_role = \
        copy.deepcopy(TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE)
    user_role["role_id"] = TEST_NOT_EXIST_ROLE_ID

    with pytest.raises(HTTPException) as e:
        assert crud_user_role.create_user_role(
            dbPgSession, schemas.FamUserRoleAssignmentCreate(**user_role), TEST_CREATOR
        )
    assert str(e._excinfo).find("Role id ") != -1
    assert str(e._excinfo).find("does not exist") != -1
    # Note, this will make sure intermediate object created by the crud call is
    #       rollback after exception is raised.
    dbPgSession.rollback()


def test_create(dbPgSession: Session):
    user_role_xref = crud_user_role.create(
        dbPgSession,
        TEST_USER_ID,
        TEST_FOM_DEV_REVIEWER_ROLE_ID,
        TEST_CREATOR
    )
    xref_dict = user_role_xref.__dict__

    # verify user role created
    found_user_role_xref = crud_user_role.get_use_role_by_user_id_and_role_id(
        dbPgSession,
        TEST_USER_ID,
        TEST_FOM_DEV_REVIEWER_ROLE_ID,
    )
    assert found_user_role_xref is not None

    # cleanup
    crud_user_role.delete_fam_user_role_assignment(
        dbPgSession,
        xref_dict["user_role_xref_id"]
    )


def test_get_use_role_by_user_id_and_role_id(dbPgSession: Session):
    # get not exists user role assignment
    found_user_role_xref = crud_user_role.get_use_role_by_user_id_and_role_id(
        dbPgSession,
        TEST_USER_ID,
        TEST_FOM_DEV_REVIEWER_ROLE_ID,
    )
    assert found_user_role_xref is None

    # create a user role assignment
    user_role_xref = crud_user_role.create(
        dbPgSession,
        TEST_USER_ID,
        TEST_FOM_DEV_REVIEWER_ROLE_ID,
        TEST_CREATOR
    )
    xref_dict = user_role_xref.__dict__

    # find it
    found_user_role_xref = crud_user_role.get_use_role_by_user_id_and_role_id(
        dbPgSession,
        TEST_USER_ID,
        TEST_FOM_DEV_REVIEWER_ROLE_ID,
    )
    assert found_user_role_xref is not None

    # cleanup
    crud_user_role.delete_fam_user_role_assignment(
        dbPgSession,
        xref_dict["user_role_xref_id"]
    )


def test_construct_forest_client_role_name():
    result = crud_user_role.construct_forest_client_role_name(
        "PARENT_ROLE",
        TEST_FOREST_CLIENT_NUMBER
    )
    assert result == "PARENT_ROLE_" + TEST_FOREST_CLIENT_NUMBER


def test_construct_forest_client_role_purpose():
    result = crud_user_role.construct_forest_client_role_purpose(
        "PARENT_ROLE purpose",
        TEST_FOREST_CLIENT_NUMBER
    )
    assert result == "PARENT_ROLE purpose for " + TEST_FOREST_CLIENT_NUMBER + ")"


def test_find_or_create_forest_client_child_role(dbPgSession: Session):
    # create child role for abstract parent role
    test_role = crud_role.get_role(dbPgSession, TEST_FOM_DEV_SUBMITTER_ROLE_ID)
    result = crud_user_role.find_or_create_forest_client_child_role(
        dbPgSession,
        TEST_FOREST_CLIENT_NUMBER,
        test_role,
        TEST_CREATOR
    )
    # verify child role created
    child_role = crud_role.get_role(dbPgSession, result.role_id)
    assert child_role.role_id == result.role_id
    assert child_role.role_name == "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER

    # create child role for concrete parent role
    test_concrete_role = crud_role.get_role(dbPgSession, TEST_FOM_DEV_REVIEWER_ROLE_ID)
    result = crud_user_role.find_or_create_forest_client_child_role(
        dbPgSession,
        TEST_FOREST_CLIENT_NUMBER,
        test_concrete_role,
        TEST_CREATOR
    )
    # verify child role created
    child_role = crud_role.get_role(dbPgSession, result.role_id)
    assert child_role.role_id == result.role_id
    assert child_role.role_name == "FOM_REVIEWER_" + TEST_FOREST_CLIENT_NUMBER
