import logging

import api.app.schemas as schemas
import pytest
from api.app.crud import crud_user_role, crud_role, crud_user
from api.app.models import model as models
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import session
from sqlalchemy import text, bindparam
from tests.fixtures.fixtures_crud_user_role_assignment import FOM_SUBMITTER_ROLE_NAME

LOGGER = logging.getLogger(__name__)


def test_createFamUserRoleXref_violate_supportUserTypes(simpleUserRoleRequest):
    # Create a user_type with not supported type.
    notSupported_UserType = "NOT_SUPPORTED_TYPE"
    requestData = simpleUserRoleRequest.dict()
    requestData["user_type"] = notSupported_UserType

    LOGGER.debug(
        "Creating user/role assignment request with not supported "
        f"user_type: {notSupported_UserType}."
    )
    with pytest.raises(ValidationError) as e:
        assert schemas.FamUserRoleAssignmentCreate(**requestData)
    assert (
        str(e.value).find(
            "value is not a valid enumeration member; permitted: 'IDIR', 'BCeID'"
        )
        != -1
    )
    LOGGER.debug(f"Expected exception raised: {e.value}")


# Make sure previous tests don't leave any role in db.
def test_roleNotExist_raise_exception(dbSession, simpleUserRoleRequest, deleteAllRoles):
    db = dbSession
    LOGGER.debug(
        "Creating user/role assignment with not supported with no role id not exist in db."
    )

    with pytest.raises(HTTPException) as e:
        assert crud_user_role.createFamUserRoleAssignment(db, simpleUserRoleRequest)
    LOGGER.debug(f"Expected exception raised: {str(e._excinfo)}")
    assert str(e._excinfo).find("Role id ") != -1
    assert str(e._excinfo).find("does not exist") != -1


def test_create_userRoleAssignment_for_forestClientFOMSubmitter(
    simpleUserRoleRequest: schemas.FamUserRoleAssignmentCreate,
    simpleFOMSubmitterRole_dbSession: session.Session,
):
    db = simpleFOMSubmitterRole_dbSession
    LOGGER.debug(
        "Creating forest client FOM Submitter user/role assignment "
        "and parent role exists in db."
    )
    famSubmitterRole = (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)
        .one_or_none()
    )
    # Verify parent role exist first.
    assert isinstance(famSubmitterRole, models.FamRole)
    assert famSubmitterRole.role_name == FOM_SUBMITTER_ROLE_NAME

    simpleUserRoleRequest.role_id = famSubmitterRole.role_id

    # User/Role assignment created.
    user_role_assignment = crud_user_role.createFamUserRoleAssignment(
        db, simpleUserRoleRequest
    )

    # Find child role
    forestClientRole = crud_role.getFamRole(db, user_role_assignment.role_id)

    # Find user by user_type and user_name
    user = crud_user.getFamUserByDomainAndName(
        db, simpleUserRoleRequest.user_type, simpleUserRoleRequest.user_name
    )

    # assert user_role_assignment, schemas.FamUserRoleAssignmentCreate
    assert user_role_assignment.role_id != famSubmitterRole.role_id
    assert forestClientRole.parent_role_id == famSubmitterRole.role_id
    assert user.user_id == user_role_assignment.user_id
    assert user.user_type == simpleUserRoleRequest.user_type

    clean_up_user_role_assignment(db, user_role_assignment)


def test_create_userRoleAssignment_for_forestClientFOMSubmitter_twice_return_existing_one(
    simpleUserRoleRequest: schemas.FamUserRoleAssignmentCreate,
    simpleFOMSubmitterRole_dbSession: session.Session,
):
    db = simpleFOMSubmitterRole_dbSession
    LOGGER.debug(
        "Creating twice forest client FOM Submitter user/role assignment "
        "will return existing record."
    )

    famSubmitterRole = (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)
        .one_or_none()
    )
    # Verify parent role exist first.
    assert isinstance(famSubmitterRole, models.FamRole)
    assert famSubmitterRole.role_name == FOM_SUBMITTER_ROLE_NAME

    simpleUserRoleRequest.role_id = famSubmitterRole.role_id

    # User/Role assignment created.
    user_role_assignment1 = crud_user_role.createFamUserRoleAssignment(
        db, simpleUserRoleRequest
    )

    # Call create twice with the same request.
    user_role_assignment2 = crud_user_role.createFamUserRoleAssignment(
        db, simpleUserRoleRequest
    )

    # Verify no extra role is created.
    parent_child_roles = set(
        (
            simpleUserRoleRequest.role_id,
            user_role_assignment1.role_id,
            user_role_assignment2.role_id,
        )
    )
    assert len(parent_child_roles) == 2  # contains only parent and child 2 roles.
    fam_roles = crud_role.getFamRoles(db)  # all db roles created.
    assert len(fam_roles) == 2

    # Verify user/role assignment creation returns the same fam_user_role_xref from db.
    assert user_role_assignment1.role_id == user_role_assignment2.role_id
    assert user_role_assignment1.user_id == user_role_assignment2.user_id
    assert (
        user_role_assignment1.user_role_xref_id
        == user_role_assignment2.user_role_xref_id
    )

    clean_up_user_role_assignment(db, user_role_assignment1)


def test_givenValidId_whenDeleteAssignment_thenUserRoleAssignmentIsDeleted(
    simpleFOMSubmitterRole_dbSession: session.Session,
):
    db = simpleFOMSubmitterRole_dbSession
    famUserRoleAssignments = (
        db.query(models.FamUserRoleXref)
        .all()
    )
    # Verify at least one record setup ready first.
    assert len(famUserRoleAssignments) >= 1

    assignment_id_to_delete = famUserRoleAssignments[0].user_role_xref_id
    crud_user_role.deleteFamUserRoleAssignment(db, assignment_id_to_delete)

    famUserRoleAssignments = (
        db.query(models.FamUserRoleXref)
        .filter(models.FamUserRoleXref.user_role_xref_id == assignment_id_to_delete)
        .one_or_none()
    )

    assert len(famUserRoleAssignments) == 1


def clean_up_user_role_assignment(
    db: session.Session, user_role_assignment: schemas.FamUserRoleAssignmentGet
):
    # Delete fam_user_role_xref
    stmt = text(
    """
        DELETE FROM fam_user_role_xref
        WHERE user_role_xref_id = :user_role_xref_id
    """
    )
    stmt = stmt.bindparams(
        bindparam("user_role_xref_id", value=user_role_assignment.user_role_xref_id)
    )
    db.execute(stmt)

    # Delete child role (db.delete(forestClientRole)).
    stmt = text(
        """
        DELETE FROM fam_role
        WHERE role_id = :role_id
    """
    )
    stmt = stmt.bindparams(bindparam("role_id", value=user_role_assignment.role_id))
    db.execute(stmt)

    # Delete user (db.delete(newUser))
    stmt = text(
        """
        DELETE FROM fam_user
        WHERE user_id = :user_id
    """
    )
    stmt = stmt.bindparams(bindparam("user_id", value=user_role_assignment.user_id))
    db.execute(stmt)
