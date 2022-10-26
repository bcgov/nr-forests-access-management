import copy
import logging

import api.app.schemas as schemas
import pytest
from api.app.crud import crud_role, crud_user, crud_user_role
from api.app.models import model as models
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import bindparam, text
from sqlalchemy.orm import session
from sqlalchemy.orm.exc import NoResultFound
from fixtures.fixtures_crud_user_role_assignment import \
    FOM_SUBMITTER_ROLE_NAME

LOGGER = logging.getLogger(__name__)


def test_createUserRoleAssignment_violate_supportUserTypes(simpleUserRoleRequest):
    # Create a user_type_code with not supported type.
    notSupported_UserType = "NS"
    requestData = simpleUserRoleRequest.dict()
    requestData["user_type_code"] = notSupported_UserType

    LOGGER.debug(
        "Creating user/role assignment request with not supported "
        f"user_type_code: {notSupported_UserType}."
    )
    with pytest.raises(ValidationError) as e:
        assert schemas.FamUserRoleAssignmentCreate(**requestData)
    assert (
        str(e.value).find(
            "value is not a valid enumeration member; permitted: 'I', 'B'"
        )
        != -1
    )
    LOGGER.debug(f"Expected exception raised: {e.value}")


# Make sure previous tests don't leave any role in db.
def test_roleNotExist_raise_exception(
    dbSession_famUserTypes: session.Session, simpleUserRoleRequest, deleteAllRoles
):
    db = dbSession_famUserTypes
    LOGGER.debug(
        "Creating user/role assignment with not supported with no role id not exist in db."
    )

    with pytest.raises(HTTPException) as e:
        assert crud_user_role.createFamUserRoleAssignment(db, simpleUserRoleRequest)
    LOGGER.debug(f"Expected exception raised: {str(e._excinfo)}")
    assert str(e._excinfo).find("Role id ") != -1
    assert str(e._excinfo).find("does not exist") != -1
    db.rollback()  # Note, this will make sure intermediate object created by the crud call is rollback after exception is raised.


def test_userRoleAssignment_withAbstractRole_raise_exception(
    simpleUserRoleRequest: schemas.FamUserRoleAssignmentCreate,
    dbSession_famUserTypes,
    simpleFOMSubmitterRole_dbSession: session.Session,
):
    db = simpleFOMSubmitterRole_dbSession
    LOGGER.debug(
        "Creating user/role assignment with role_type_code is 'A' (abstract role)"
        ", cannot be created."
    )

    famSubmitterRole = (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)
        .one_or_none()
    )
    # Verify this role is 'abstract' first.
    assert famSubmitterRole.role_type_code == models.FamRoleType.ROLE_TYPE_ABSTRACT

    invalid_request = copy.deepcopy(simpleUserRoleRequest)
    invalid_request.role_id = famSubmitterRole.role_id
    # test on creating assignment with abstract role, no need to
    # provide forest_client_number
    del invalid_request.forest_client_number

    with pytest.raises(HTTPException) as e:
        assert crud_user_role.createFamUserRoleAssignment(db, invalid_request)
    LOGGER.debug(f"Expected exception raised: {str(e._excinfo)}")
    assert str(e._excinfo).find("Cannot assign") != -1
    db.rollback()


def test_create_userRoleAssignment_for_forestClientFOMSubmitter(
    simpleUserRoleRequest: schemas.FamUserRoleAssignmentCreate,
    dbSession_famUserTypes,
    simpleFOMSubmitterRole_dbSession: session.Session,
):
    db = simpleFOMSubmitterRole_dbSession
    LOGGER.debug(
        "Creating forest client FOM Submitter user/role assignment "
        "and parent role exists in db."
    )
    fomSubmitterRole = (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)
        .one_or_none()
    )
    # Verify parent role exist first.
    assert isinstance(fomSubmitterRole, models.FamRole)
    assert fomSubmitterRole.role_name == FOM_SUBMITTER_ROLE_NAME
    assert fomSubmitterRole.role_type_code == models.FamRoleType.ROLE_TYPE_ABSTRACT

    simpleUserRoleRequest.role_id = fomSubmitterRole.role_id

    # User/Role assignment created.
    user_role_assignment = crud_user_role.createFamUserRoleAssignment(
        db, simpleUserRoleRequest
    )

    # Find child role
    forestClientRole = crud_role.getFamRole(db, user_role_assignment.role_id)

    # Find user by user_type_code and user_name
    user = crud_user.getFamUserByDomainAndName(
        db, simpleUserRoleRequest.user_type_code, simpleUserRoleRequest.user_name
    )

    # assert user_role_assignment, schemas.FamUserRoleAssignmentCreate
    assert user_role_assignment.role_id != fomSubmitterRole.role_id
    assert forestClientRole.parent_role_id == fomSubmitterRole.role_id
    assert user.user_id == user_role_assignment.user_id
    assert user.user_type_code == simpleUserRoleRequest.user_type_code
    assert forestClientRole.role_type_code == models.FamRoleType.ROLE_TYPE_CONCRETE

    clean_up_user_role_assignment(db, user_role_assignment)


def test_create_userRoleAssignment_for_forestClientFOMSubmitter_twice_return_existing_one(
    simpleUserRoleRequest: schemas.FamUserRoleAssignmentCreate,
    dbSession_famUserTypes,
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
    simpleUserRoleAssignment_dbSession: session.Session,
):
    db = simpleUserRoleAssignment_dbSession
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

    # Verify correct user/role assignment has been deleted.
    assert famUserRoleAssignments is None


def test_givenInValidId_whenDeleteAssignment_raiseException(
    simpleUserRoleAssignment_dbSession: session.Session,
):
    db = simpleUserRoleAssignment_dbSession
    famUserRoleAssignments = (
        db.query(models.FamUserRoleXref)
        .all()
    )
    # Verify  one record setup ready first.
    assert len(famUserRoleAssignments) == 1

    with pytest.raises(NoResultFound) as e:
        invalid_id = 0
        crud_user_role.deleteFamUserRoleAssignment(db, invalid_id)
    LOGGER.debug(f"Expected exception raised: {str(e._excinfo)}")
    assert str(e._excinfo).find("No row was found when one was required") != -1


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

    # Then delete parent role
    stmt = text(
        """
        DELETE FROM fam_role
    """
    )
    # stmt = stmt.bindparams(bindparam("role_id", value=user_role_assignment.role_id))
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
