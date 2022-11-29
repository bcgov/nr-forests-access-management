import logging

import api.app.schemas as schemas
import pytest
from api.app.crud import crud_role
from sqlalchemy.exc import IntegrityError

LOGGER = logging.getLogger(__name__)


def test_getFamRoles_nodata(dbSession):
    famRoles = crud_role.getFamRoles(dbSession)
    LOGGER.debug(f"fam roles: {famRoles}")
    assert famRoles == []


def test_getFamRoles_withdata(dbSession_famRoles_concrete, concreteRoleData):
    db = dbSession_famRoles_concrete
    roles = crud_role.getFamRoles(db)
    LOGGER.debug(f"roles: {roles}")
    LOGGER.debug(f"number of roles: {len(roles)}")
    # expecting the number of records in the role table to be 1
    assert 1 == len(roles)

    # checking that the expected role is in the db
    for role in roles:
        LOGGER.debug(f"role: {role.__dict__} {role.role_name}")
        assert role.role_name == concreteRoleData["role_name"]


def test_createSimpleFamRole(
    concreteRoleData_asPydantic, dbSession_famRoletype, deleteAllRoles
):
    db = dbSession_famRoletype
    LOGGER.debug(
        f"simpleRoleData_asPydantic: {concreteRoleData_asPydantic}"
    )

    # get role count
    rolesBefore = crud_role.getFamRoles(db)
    numRolesStart = len(rolesBefore)

    role = crud_role.createFamRole(famRole=concreteRoleData_asPydantic, db=db)
    LOGGER.debug(f"created the role: {role}")

    # make sure the role that was created has the same role_name as the supplied
    assert role.role_name == concreteRoleData_asPydantic.role_name

    rolesAfter = crud_role.getFamRoles(db)
    numRolesAfter = len(rolesAfter)
    assert numRolesAfter > numRolesStart


def test_createFamRole_withExistingRoleName_violate_constraint(
    concreteRoleData_asPydantic, dbSession_famRoletype, deleteAllRoleTypes
):
    db = dbSession_famRoletype

    # Add simple role
    role = crud_role.createFamRole(famRole=concreteRoleData_asPydantic, db=db)
    LOGGER.debug(f"New role is added: {role.role_name} role.")

    # Verify new role
    roles = crud_role.getFamRoles(db)
    filtered = list(filter(lambda role:
                    role.role_name == concreteRoleData_asPydantic.role_name,
                    roles))
    assert len(filtered) == 1

    # Add same role => expect constraint violation
    LOGGER.debug(f"Adding role {concreteRoleData_asPydantic.role_name} again.")
    with pytest.raises(IntegrityError) as e:
        # invalid insert for the same role.
        assert crud_role.createFamRole(famRole=concreteRoleData_asPydantic, db=db)
    assert str(e.value).find("UNIQUE constraint failed: fam_role.role_name") != -1
    # if don't rollback the exception leaves the database session in an unstable
    # state and subsequent commits / flush statements will fail
    db.rollback()
    LOGGER.debug(f"Expected exception raised: {e.value}")


def test_createFamRole_withParentRole(
    concreteRoleData_asPydantic, dbSession_famRoletype, deleteAllRoles
):
    db = dbSession_famRoletype

    # Set up ROLE_PARENT
    ROLE_PARENT = "ROLE_PARENT"
    parentRoleData = concreteRoleData_asPydantic.dict()
    parentRoleData["role_name"] = ROLE_PARENT
    LOGGER.debug(f"Adding role: {parentRoleData}.")
    parentRole = crud_role.createFamRole(famRole=schemas.FamRoleCreate(**parentRoleData), db=db)

    assert parentRole.role_name == ROLE_PARENT
    assert parentRole.role_id > 0
    LOGGER.debug(f"Parent role added. role_id: {parentRole.role_id}")

    # Add ROLE_CHILD associated with ROLE_PARENT
    ROLE_CHILD = "ROLE_CHILD"
    childRoleData = concreteRoleData_asPydantic.dict()
    childRoleData["role_name"] = ROLE_CHILD
    childRoleData["parent_role_id"] = parentRole.role_id
    LOGGER.debug(f"Adding role: {childRoleData}.")
    childRole = crud_role.createFamRole(famRole=schemas.FamRoleCreate(**childRoleData), db=db)

    assert childRole.role_name == ROLE_CHILD
    assert childRole.role_id > 0 and childRole.role_id != parentRole.role_id
    assert childRole.parent_role_id == parentRole.role_id
    LOGGER.debug(f"Child role added: {vars(childRole)}")


def test_createFamRole_withNoneExistingParentRole_violate_constraint(
    concreteRoleData_asPydantic, dbSession_famRoletype
):
    db = dbSession_famRoletype

    # Create a role with non-existing parent_role_id
    none_existing_parent_role_id = 999
    roleData = concreteRoleData_asPydantic.dict()
    roleData["parent_role_id"] = none_existing_parent_role_id

    famRole = schemas.FamRoleCreate(**roleData)
    LOGGER.debug(f"Adding role with non-existing parent_role_id-: {famRole}.")
    with pytest.raises(IntegrityError) as e:
        # invalid insert for the same role.
        assert crud_role.createFamRole(famRole, db=db)
    assert str(e.value).find("FOREIGN KEY constraint failed") != -1
    LOGGER.debug(f"Expected exception raised: {e.value}")
