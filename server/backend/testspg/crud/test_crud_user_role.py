import os
import sys
from sqlalchemy.orm import Session
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from api.app.crud import crud_user_role, crud_role
from testspg.constants import TEST_FOM_DEV_REVIEWER_ROLE_ID, \
    TEST_FOM_DEV_SUBMITTER_ROLE_ID, \
    TEST_CREATOR

LOGGER = logging.getLogger(__name__)

TEST_USER_ID = 1
TEST_FOREST_CLIENT_NUMBER = "00000001"


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
