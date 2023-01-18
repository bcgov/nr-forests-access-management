import logging
import copy
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import session
from api.app import constants

import api.app.models.model as model
import api.app.schemas as schemas
from api.app.crud import crud_forest_client, crud_role

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
    concrete_role_pydantic: schemas.FamRoleCreate, 
    dbsession_role_types, 
    dbsession_application, 
    delete_all_roles
):
    db = dbsession_application
    LOGGER.debug(f"simpleRoleData_asPydantic: {concrete_role_pydantic}")

    # get role count
    roles_before = crud_role.get_roles(db)
    num_roles_start = len(roles_before)
    application: model.FamApplication = db.query(model.FamApplication).one()
    concrete_role_pydantic.application_id = application.application_id

    role = crud_role.create_role(role=concrete_role_pydantic, db=db)
    LOGGER.debug(f"created the role: {role}")

    # make sure the role that was created has the same role_name as the supplied
    assert role.role_name == concrete_role_pydantic.role_name

    roles_after = crud_role.get_roles(db)
    num_roles_after = len(roles_after)
    assert num_roles_after > num_roles_start


def test_create_role_with_parent_role(
    concrete_role_pydantic, 
    dbsession_role_types,
    dbsession_application, 
    delete_all_roles
):
    db = dbsession_application
    application: model.FamApplication = db.query(model.FamApplication).one()

    # Set up ROLE_PARENT
    ROLE_PARENT = "ROLE_PARENT"
    parent_role_data = concrete_role_pydantic.dict()
    parent_role_data["role_name"] = ROLE_PARENT
    parent_role_data["application_id"] = application.application_id
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
    child_role_data["application_id"] = application.application_id
    LOGGER.debug(f"Adding role: {child_role_data}.")
    child_role = crud_role.create_role(
        role=schemas.FamRoleCreate(**child_role_data), db=db
    )

    assert child_role.role_name == ROLE_CHILD
    assert child_role.role_id > 0 and child_role.role_id != parent_role.role_id
    assert child_role.parent_role_id == parent_role.role_id
    LOGGER.debug(f"Child role added: {vars(child_role)}")


def test_create_fam_role_with_forest_client(
        concrete_role_with_forest_client,
        dbsession_application,
        dbsession_role_types):
    db = dbsession_role_types
    application: model.FamApplication = db.query(model.FamApplication).one()
    role_data = concrete_role_with_forest_client

    # double check that the forest client number field is populated as
    # that is core to this test
    assert role_data['forest_client_number'] is not None

    # testing that the data can be converted to pydantic model
    fam_role_as_pydantic = schemas.FamRoleCreate(**role_data)
    fam_role_as_pydantic.application_id = application.application_id

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


def test_can_create_roles_with_same_name_different_applications(
    concrete_role_pydantic: schemas.FamRoleCreate, 
    dbsession_role_types, 
    dbsession_application: session.Session
):
    db = dbsession_application
    application_1: model.FamApplication = db.query(model.FamApplication).one()
    concrete_role_pydantic.application_id = application_1.application_id

    # Add first role
    role = crud_role.create_role(role=concrete_role_pydantic, db=db)
    LOGGER.debug(f"created the role: {role}")
    roles_before = crud_role.get_roles(db)
    num_roles_start = len(roles_before)
    assert num_roles_start == 1
    role_1 = roles_before[0]
    assert role_1.role_name == concrete_role_pydantic.role_name

    # Create second application
    application_2_dict = copy.deepcopy(dict(application_1.__dict__))
    application_2_dict.pop('_sa_instance_state', None)
    application_2_dict.pop('application_id', None)
    application_2_dict['application_name'] = 'Second Application'
    application_2_db_item = model.FamApplication(**application_2_dict)
    db.add(application_2_db_item)
    db.flush()
    LOGGER.info(f"second FamApplication added: {application_2_db_item.__dict__}")
    assert application_2_db_item.application_id != application_1.application_id

    # Create second role (same role name) for second application.
    role_2_pydantic = schemas.FamRoleCreate(**{
        "role_name": role.role_name,
        "role_purpose": "Role Purpose for Second Role",
        "create_user": constants.FAM_PROXY_API_USER,
        "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
    })
    role_2_pydantic.application_id = application_2_db_item.application_id
    role_2 = crud_role.create_role(role=role_2_pydantic, db=db)
    LOGGER.debug(f"created the role: {role_2}")

    # Verify role1 and role2
    roles_after = crud_role.get_roles(db)
    num_roles_after = len(roles_after)
    assert num_roles_after == 2
    assert role_2.application_id != role_1.application_id
    assert role_2.role_name == role_1.role_name
    assert role_2.role_id != role_1.role_id

    # clean up
    db.delete(application_2_db_item)
    roles = crud_role.get_roles(db)
    for role in roles:
        db.delete(role)


def test_create_role_with_no_existing_parent_role_violate_constraint(
    concrete_role_pydantic, dbsession_role_types, dbsession_application
):
    db: session.Session = dbsession_application
    db.commit()
    application: model.FamApplication = db.query(model.FamApplication).one()

    # Create a role with non-existing parent_role_id
    none_existing_parent_role_id = 999
    role_data = concrete_role_pydantic.dict()
    role_data["parent_role_id"] = none_existing_parent_role_id
    role_data["application_id"] = application.application_id

    fam_role = schemas.FamRoleCreate(**role_data)
    LOGGER.debug(f"Adding role with non-existing parent_role_id-: {fam_role}.")
    with pytest.raises(IntegrityError) as e:
        # invalid insert for the same role.
        assert crud_role.create_role(role=fam_role, db=db)
    assert str(e.value).find("FOREIGN KEY constraint failed") != -1
    db.rollback()
    LOGGER.debug(f"Expected exception raised: {e.value}")

    
def test_create_role_with_same_role_name_and_application_violate_constraint(
    concrete_role_pydantic: schemas.FamRoleCreate, 
    dbsession_role_types, 
    dbsession_application, 
    delete_all_role_types
):
    db = dbsession_application
    db.commit()
    application: model.FamApplication = db.query(model.FamApplication).one()
    concrete_role_pydantic.application_id = application.application_id

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
    assert str(e.value).find("UNIQUE constraint failed: fam_role.role_name, fam_role.application_id") != -1
    db.rollback()
    LOGGER.debug(f"Expected exception raised: {e.value}")