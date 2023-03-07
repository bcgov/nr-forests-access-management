import copy
import logging

import api.app.schemas as schemas
import pytest
from api.app.crud import crud_role, crud_user, crud_user_role
from api.app.models import model as models
import api.app.constants as constants
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import bindparam, text
from sqlalchemy.orm import session
from sqlalchemy.orm.exc import NoResultFound
from tests.fixtures.fixtures_crud_user_role_assignment import FOM_SUBMITTER_ROLE_NAME  # noqa

LOGGER = logging.getLogger(__name__)


def test_create_user_role_assignment_violate_support_user_types(
    user_role_assignment_model,
):
    # Create a user_type_code with not supported type.
    not_supported_user_type = "NS"
    request_data = user_role_assignment_model.dict()
    request_data["user_type_code"] = not_supported_user_type

    LOGGER.debug(
        "Creating user/role assignment request with not supported "
        f"user_type_code: {not_supported_user_type}."
    )
    with pytest.raises(ValidationError) as e:
        assert schemas.FamUserRoleAssignmentCreate(**request_data)
    assert (
        str(e.value).find(
            "value is not a valid enumeration member; permitted: 'I', 'B'"
        )
        != -1
    )
    LOGGER.debug(f"Expected exception raised: {e.value}")


# Make sure previous tests don't leave any role in db.
def test_role_not_exist_raise_exception(
    dbsession_fam_user_types: session.Session,
    user_role_assignment_model,
    delete_all_roles,
):
    db = dbsession_fam_user_types
    LOGGER.debug(
        "Creating user/role assignment with not supported with no role id not" +
        " exist in db."
    )

    with pytest.raises(HTTPException) as e:
        assert crud_user_role.create_user_role(
            db, user_role_assignment_model, constants.FAM_PROXY_API_USER
        )
    LOGGER.debug(f"Expected exception raised: {str(e._excinfo)}")
    assert str(e._excinfo).find("Role id ") != -1
    assert str(e._excinfo).find("does not exist") != -1
    # Note, this will make sure intermediate object created by the crud call is
    #       rollback after exception is raised.
    db.rollback()


def test_user_role_assignment_with_abstract_role_raise_exception(
    user_role_assignment_model: schemas.FamUserRoleAssignmentCreate,
    dbsession_fam_user_types,
    dbsession_FOM_submitter_role: session.Session,  # noqa NOSONAR
):
    db = dbsession_FOM_submitter_role
    LOGGER.debug(
        "Creating user/role assignment with role_type_code is 'A' (abstract role)"
        ", cannot be created."
    )

    fam_submitter_role = (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)
        .one_or_none()
    )
    # Verify this role is 'abstract' first.
    assert fam_submitter_role.role_type_code == constants.RoleType.ROLE_TYPE_ABSTRACT

    invalid_request = copy.deepcopy(user_role_assignment_model)
    invalid_request.role_id = fam_submitter_role.role_id
    # test on creating assignment with abstract role, no need to
    # provide forest_client_number
    del invalid_request.forest_client_number

    with pytest.raises(HTTPException) as e:
        assert crud_user_role.create_user_role(db, invalid_request, constants.FAM_PROXY_API_USER)
    LOGGER.debug(f"Expected exception raised: {str(e._excinfo)}")
    assert str(e._excinfo).find("Cannot assign") != -1
    db.rollback()


def test_create_user_role_assignment_for_forest_client_FOM_submitter(  # NOSONAR
    user_role_assignment_model: schemas.FamUserRoleAssignmentCreate,
    dbsession_fam_user_types,
    dbsession_FOM_submitter_role: session.Session,  # noqa NOSONAR
):
    db = dbsession_FOM_submitter_role
    LOGGER.debug(
        "Creating forest client FOM Submitter user/role assignment "
        "and parent role exists in db."
    )
    fom_submitter_role = (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)
        .one_or_none()
    )
    # Verify parent role exist first.
    assert isinstance(fom_submitter_role, models.FamRole)
    assert fom_submitter_role.role_name == FOM_SUBMITTER_ROLE_NAME
    assert fom_submitter_role.role_type_code == constants.RoleType.ROLE_TYPE_ABSTRACT

    user_role_assignment_model.role_id = fom_submitter_role.role_id

    # User/Role assignment created.
    user_role_assignment = crud_user_role.create_user_role(
        db, user_role_assignment_model, constants.FAM_PROXY_API_USER
    )

    # Find child role
    forest_client_role = crud_role.get_role(db, user_role_assignment.role_id)

    # Find user by user_type_code and user_name
    user = crud_user.get_user_by_domain_and_name(
        db,
        user_role_assignment_model.user_type_code,
        user_role_assignment_model.user_name,
    )

    assert user_role_assignment.role_id != fom_submitter_role.role_id
    assert forest_client_role.parent_role_id == fom_submitter_role.role_id
    assert user.user_id == user_role_assignment.user_id
    assert user.user_type_code == user_role_assignment_model.user_type_code
    assert forest_client_role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE

    clean_up_user_role_assignment(db, user_role_assignment)


def test_create_user_role_assignment_for_forest_client_FOM_submitter_twice_raises_exception( # noqa NOSONAR
    user_role_assignment_model: schemas.FamUserRoleAssignmentCreate,
    dbsession_fam_user_types,
    dbsession_FOM_submitter_role: session.Session,  # noqa NOSONAR
):
    db = dbsession_FOM_submitter_role
    LOGGER.debug(
        "Creating twice forest client FOM Submitter user/role assignment "
        "will raise an exception."
    )

    fam_submitter_role = (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)
        .one_or_none()
    )
    # Verify parent role exist first.
    assert isinstance(fam_submitter_role, models.FamRole)
    assert fam_submitter_role.role_name == FOM_SUBMITTER_ROLE_NAME

    user_role_assignment_model.role_id = fam_submitter_role.role_id

    # User/Role assignment created.
    user_role_assignment1 = crud_user_role.create_user_role(
        db, user_role_assignment_model, constants.FAM_PROXY_API_USER
    )

    # Call create twice with the same request.
    with pytest.raises(HTTPException) as e:
        crud_user_role.create_user_role(
            db, user_role_assignment_model, constants.FAM_PROXY_API_USER
        )

    LOGGER.debug(f"Expected exception raised: {str(e._excinfo)}")
    fam_roles = crud_role.get_roles(db)  # all db roles created.
    assert len(fam_roles) == 2

    clean_up_user_role_assignment(db, user_role_assignment1)


def test_given_valid_id_when_delete_assignment_then_user_role_assignment_is_deleted(  # noqa NOSONAR
    dbsession_user_role_assignment: session.Session,
):
    db = dbsession_user_role_assignment
    fam_user_role_assignments = db.query(models.FamUserRoleXref).all()
    # Verify at least one record setup ready first.
    assert len(fam_user_role_assignments) >= 1

    assignment_id_to_delete = fam_user_role_assignments[0].user_role_xref_id
    crud_user_role.delete_fam_user_role_assignment(db, assignment_id_to_delete)

    fam_user_role_assignments = (
        db.query(models.FamUserRoleXref)
        .filter(models.FamUserRoleXref.user_role_xref_id == assignment_id_to_delete)
        .one_or_none()
    )

    # Verify correct user/role assignment has been deleted.
    assert fam_user_role_assignments is None


def test_given_invalid_id_when_delete_assignment_raise_exception(
    dbsession_user_role_assignment: session.Session,
):
    db = dbsession_user_role_assignment
    fam_user_role_assignments = db.query(models.FamUserRoleXref).all()
    # Verify  one record setup ready first.
    assert len(fam_user_role_assignments) == 1

    with pytest.raises(NoResultFound) as e:
        invalid_id = 0
        crud_user_role.delete_fam_user_role_assignment(db, invalid_id)
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

    # Delete child role (db.delete(forest_client_role)).
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
    # stmt = stmt.bindparams(bindparam("role_id", value=user_role_assignment.role_id))  # noqa NOSONAR
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
