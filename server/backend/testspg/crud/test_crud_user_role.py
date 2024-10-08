import copy
import logging

import pytest
from api.app.crud import crud_role, crud_user_role
from api.app.schemas import FamUserRoleAssignmentCreateSchema, TargetUserSchema
from api.app.schemas.requester import RequesterSchema
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session
from testspg.constants import (ACCESS_GRANT_FOM_DEV_CR_IDIR,
                               FOM_DEV_REVIEWER_ROLE_ID,
                               FOM_DEV_SUBMITTER_ROLE_ID, NOT_EXIST_ROLE_ID,
                               TEST_CREATOR, TEST_NOT_EXIST_USER_TYPE,
                               TEST_USER_GUID_IDIR, TEST_USER_NAME_IDIR)

LOGGER = logging.getLogger(__name__)

TEST_USER_ID = 1
TEST_FOREST_CLIENT_NUMBER = "00000001"


def test_create_user_role_with_role_not_exists(db_pg_session: Session):
    user_role = copy.deepcopy(ACCESS_GRANT_FOM_DEV_CR_IDIR)
    user_role["role_id"] = NOT_EXIST_ROLE_ID
    dummy_test_requester = RequesterSchema(**{
        "cognito_user_id": TEST_CREATOR,
        "user_name": TEST_USER_NAME_IDIR,
        "user_guid":  TEST_USER_GUID_IDIR,
        "user_id": TEST_USER_ID
    })

    with pytest.raises(HTTPException) as e:

        mocked_target_user = TargetUserSchema(**user_role)
        assert crud_user_role.create_user_role_assignment_many(
            db_pg_session,
            FamUserRoleAssignmentCreateSchema(**user_role),
            mocked_target_user,
            dummy_test_requester
        )
    assert str(e._excinfo).find("Role id ") != -1
    assert str(e._excinfo).find("does not exist") != -1


def test_create_user_role_with_user_types_not_exists(db_pg_session: Session):
    # Create a user_type_code with not supported type.
    user_role = copy.deepcopy(ACCESS_GRANT_FOM_DEV_CR_IDIR)
    user_role["user_type_code"] = TEST_NOT_EXIST_USER_TYPE

    with pytest.raises(ValidationError) as e:
        assert FamUserRoleAssignmentCreateSchema(**user_role)
    assert str(e.value).find("Input should be 'I' or 'B'") != -1
    LOGGER.debug(f"Expected exception raised: {e.value}")


def test_create(db_pg_session: Session):
    crud_user_role.create(
        db_pg_session, TEST_USER_ID, FOM_DEV_REVIEWER_ROLE_ID, TEST_CREATOR
    )

    # verify user role created
    found_user_role_xref = crud_user_role.get_use_role_by_user_id_and_role_id(
        db_pg_session,
        TEST_USER_ID,
        FOM_DEV_REVIEWER_ROLE_ID,
    )
    assert found_user_role_xref is not None


def test_get_use_role_by_user_id_and_role_id(db_pg_session: Session):
    # get not exists user role assignment
    found_user_role_xref = crud_user_role.get_use_role_by_user_id_and_role_id(
        db_pg_session,
        TEST_USER_ID,
        FOM_DEV_REVIEWER_ROLE_ID,
    )
    assert found_user_role_xref is None

    # create a user role assignment
    crud_user_role.create(
        db_pg_session, TEST_USER_ID, FOM_DEV_REVIEWER_ROLE_ID, TEST_CREATOR
    )

    # find it
    found_user_role_xref = crud_user_role.get_use_role_by_user_id_and_role_id(
        db_pg_session,
        TEST_USER_ID,
        FOM_DEV_REVIEWER_ROLE_ID,
    )
    assert found_user_role_xref is not None


def test_construct_forest_client_role_name():
    result = crud_user_role.construct_forest_client_role_name(
        "PARENT_ROLE", TEST_FOREST_CLIENT_NUMBER
    )
    assert result == "PARENT_ROLE_" + TEST_FOREST_CLIENT_NUMBER


def test_construct_forest_client_role_purpose():
    result = crud_user_role.construct_forest_client_role_purpose(
        "PARENT_ROLE purpose", TEST_FOREST_CLIENT_NUMBER
    )
    assert result == "PARENT_ROLE purpose for " + TEST_FOREST_CLIENT_NUMBER


def test_find_or_create_forest_client_child_role(db_pg_session: Session):
    # create child role for abstract parent role
    test_role = crud_role.get_role(db_pg_session, FOM_DEV_SUBMITTER_ROLE_ID)
    result = crud_user_role.find_or_create_forest_client_child_role(
        db_pg_session, TEST_FOREST_CLIENT_NUMBER, test_role, TEST_CREATOR
    )
    # verify child role created
    child_role_one = crud_role.get_role(db_pg_session, result.role_id)
    assert child_role_one.role_id == result.role_id
    assert child_role_one.role_name == "FOM_SUBMITTER_" + TEST_FOREST_CLIENT_NUMBER

    # create child role for concrete parent role
    test_concrete_role = crud_role.get_role(db_pg_session, FOM_DEV_REVIEWER_ROLE_ID)
    result = crud_user_role.find_or_create_forest_client_child_role(
        db_pg_session, TEST_FOREST_CLIENT_NUMBER, test_concrete_role, TEST_CREATOR
    )
    # verify child role created
    child_role_two = crud_role.get_role(db_pg_session, result.role_id)
    assert child_role_two.role_id == result.role_id
    assert child_role_two.role_name == "FOM_REVIEWER_" + TEST_FOREST_CLIENT_NUMBER
