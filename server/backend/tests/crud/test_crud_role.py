import logging

import api.app.schemas as schemas
import pytest
from api.app.crud import crud_role
from api.app.crud import crud_forest_client
from sqlalchemy.exc import IntegrityError

LOGGER = logging.getLogger(__name__)


def test_get_roles_nodata(dbsession):
    fam_roles = crud_role.get_roles(dbsession)
    LOGGER.debug(f"fam roles: {fam_roles}")
    assert fam_roles == []


def test_get_roles_withdata(dbsession_fam_roles_concrete, concrete_role_dict):
    db = dbsession_fam_roles_concrete
    roles = crud_role.get_roles(db)
    LOGGER.debug(f"roles: {roles}")
    LOGGER.debug(f"number of roles: {len(roles)}")
    # expecting the number of records in the role table to be 1
    assert 1 == len(roles)

    # checking that the expected role is in the db
    for role in roles:
        LOGGER.debug(f"role: {role.__dict__} {role.role_name}")
        assert role.role_name == concrete_role_dict["role_name"]


def test_create_role(
    concrete_role_pydantic, dbsession_role_types, delete_all_roles
):
    db = dbsession_role_types
    LOGGER.debug(f"simpleRoleData_asPydantic: {concrete_role_pydantic}")

    # get role count
    roles_before = crud_role.get_roles(db)
    num_roles_start = len(roles_before)

    role = crud_role.create_role(role=concrete_role_pydantic, db=db)
    LOGGER.debug(f"created the role: {role}")

    # make sure the role that was created has the same role_name as the supplied
    assert role.role_name == concrete_role_pydantic.role_name

    roles_after = crud_role.get_roles(db)
    num_roles_after = len(roles_after)
    assert num_roles_after > num_roles_start


def test_create_role_with_existing_role_name_violate_constraint(
    concrete_role_pydantic, dbsession_role_types, delete_all_role_types
):
    db = dbsession_role_types

    # Add simple role
    role = crud_role.create_role(role=concrete_role_pydantic, db=db)
    LOGGER.debug(f"New role is added: {role.role_name} role.")

    # Verify new role
    roles = crud_role.get_roles(db)
    filtered = list(
        filter(
            lambda role: role.role_name == concrete_role_pydantic.role_name, roles
        )
    )
    assert len(filtered) == 1

    # Add same role => expect constraint violation
    LOGGER.debug(f"Adding role {concrete_role_pydantic.role_name} again.")
    with pytest.raises(IntegrityError) as e:
        # invalid insert for the same role.
        assert crud_role.create_role(role=concrete_role_pydantic, db=db)
    assert str(e.value).find("UNIQUE constraint failed: fam_role.role_name") != -1
    # if don't rollback the exception leaves the database session in an unstable
    # state and subsequent commits / flush statements will fail
    db.rollback()
    LOGGER.debug(f"Expected exception raised: {e.value}")


def test_create_role_with_parent_role(
    concrete_role_pydantic, dbsession_role_types, delete_all_roles
):
    db = dbsession_role_types

    # Set up ROLE_PARENT
    ROLE_PARENT = "ROLE_PARENT"
    parent_role_data = concrete_role_pydantic.dict()
    parent_role_data["role_name"] = ROLE_PARENT
    LOGGER.debug(f"Adding role: {parent_role_data}.")
    parent_role = crud_role.create_role(
        role=schemas.FamRoleCreate(**parent_role_data), db=db
    )

    assert parent_role.role_name == ROLE_PARENT
    assert parent_role.role_id > 0
    LOGGER.debug(f"Parent role added. role_id: {parent_role.role_id}")

    # Add ROLE_CHILD associated with ROLE_PARENT
    ROLE_CHILD = "ROLE_CHILD"
    child_role_data = concrete_role_pydantic.dict()
    child_role_data["role_name"] = ROLE_CHILD
    child_role_data["parent_role_id"] = parent_role.role_id
    LOGGER.debug(f"Adding role: {child_role_data}.")
    child_role = crud_role.create_role(
        role=schemas.FamRoleCreate(**child_role_data), db=db
    )

    assert child_role.role_name == ROLE_CHILD
    assert child_role.role_id > 0 and child_role.role_id != parent_role.role_id
    assert child_role.parent_role_id == parent_role.role_id
    LOGGER.debug(f"Child role added: {vars(child_role)}")


def test_create_role_with_no_existing_parent_role_violate_constraint(
    concrete_role_pydantic, dbsession_role_types
):
    db = dbsession_role_types

    # Create a role with non-existing parent_role_id
    none_existing_parent_role_id = 999
    role_data = concrete_role_pydantic.dict()
    role_data["parent_role_id"] = none_existing_parent_role_id

    fam_role = schemas.FamRoleCreate(**role_data)
    LOGGER.debug(f"Adding role with non-existing parent_role_id-: {fam_role}.")
    with pytest.raises(IntegrityError) as e:
        # invalid insert for the same role.
        assert crud_role.create_role(role=fam_role, db=db)
    assert str(e.value).find("FOREIGN KEY constraint failed") != -1
    LOGGER.debug(f"Expected exception raised: {e.value}")


def test_create_fam_role_with_forest_client(
        concrete_role_with_forest_client,
        dbsession_role_types):
    db = dbsession_role_types
    role_data = concrete_role_with_forest_client

    # double check that the forest client number field is populated as
    # that is core to this test
    assert role_data['forest_client_number'] is not None

    # testing that the data can be converted to pydantic model
    fam_role_as_pydantic = schemas.FamRoleCreate(**role_data)

    # add the role with forest client to the database
    role_in_db = crud_role.create_role(role=fam_role_as_pydantic, db=db)
    LOGGER.debug(f"role from db: {role_in_db}")

    # make a separate query to the database for all the roles (should only be
    # the one)
    roles = crud_role.get_roles(db)
    LOGGER.debug("roles from the database: {roles}")
    assert len(roles) == 1
    # assert that the data retured from the database is the same as the data
    # that was used to create the database record
    assert roles[0].role_name == role_data['role_name']
    assert (
        roles[0].client_number.forest_client_number ==
        role_data['forest_client_number']
    )
    assert roles[0].role_type_code == role_data['role_type_code']
    assert roles[0].create_user == role_data['create_user']
    LOGGER.debug(f"forest client number: {role_data['forest_client_number']}")

    # make sure that a forest client record exists in the database
    forest_client_from_db = crud_forest_client.get_forest_client(
        db=db, forest_client_number=role_data['forest_client_number'])
    assert (
        forest_client_from_db.forest_client_number ==
        role_data['forest_client_number']
    )

    # cleanup the roles that have been created in this test
    #  db.delete(roles[0].client_number)
    db.delete(roles[0])
