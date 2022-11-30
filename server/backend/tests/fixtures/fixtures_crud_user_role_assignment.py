import logging

import api.app.constants as famConstants
import api.app.models.model as model
import api.app.schemas as schemas
import pytest
from sqlalchemy import text
from sqlalchemy.orm import session

LOGGER = logging.getLogger(__name__)

FOM_SUBMITTER_ROLE_NAME = "FOM_Submitter"


@pytest.fixture(scope="function")
def simpleUserRoleData() -> dict:
    userRoleData = {
        "user_name": "Test User",
        "user_type_code": famConstants.UserType.BCEID,
        "role_id": 2,
        "forest_client_number": "00001001",
    }
    yield userRoleData


@pytest.fixture(scope="function")
def simpleUserRoleRequest(simpleUserRoleData) -> schemas.FamUserRoleAssignmentCreate:
    famUserRoleRequest = schemas.FamUserRoleAssignmentCreate(**simpleUserRoleData)
    yield famUserRoleRequest


@pytest.fixture(scope="function")
def simpleUserRoleAssignment_dbSession(
    request, dbsession_fam_user_types, simpleFOMSubmitterRole_dbSession: session.Session
):
    db = simpleFOMSubmitterRole_dbSession
    fam_role: model.FamRole = (db.query(model.FamRole).all())[0]

    # add dummy user
    fam_user = model.FamUser(
        **{
            "user_type_code": famConstants.UserType.IDIR,
            "user_name": famConstants.DUMMY_FOREST_CLIENT_NAME,
            "create_user": famConstants.FAM_PROXY_API_USER,
        }
    )
    db.add(fam_user)
    db.flush()

    # add user/role assignment
    user_role_assignment = model.FamUserRoleXref(
        **{
            "user_id": fam_user.user_id,
            "role_id": fam_role.role_id,
            "create_user": famConstants.FAM_PROXY_API_USER,
        }
    )
    db.add(user_role_assignment)
    db.commit()
    yield db

    xref_db_item = (
        db.query(model.FamUserRoleXref)
        .filter(
            model.FamUserRoleXref.user_id == user_role_assignment.user_id,
            model.FamUserRoleXref.role_id == user_role_assignment.role_id,
        )
        .one_or_none()
    )

    if xref_db_item:
        db.delete(xref_db_item)
    db.delete(fam_user)
    db.commit()


@pytest.fixture(scope="function")
def simpleFamApplication_dbSession(dbSession):
    db = dbSession
    famApplication = model.FamApplication(
        **{
            "application_name": "FOM",
            "application_description": "Forest Operations Map",
            "create_user": famConstants.FAM_PROXY_API_USER,
        }
    )
    db.add(famApplication)
    db.commit()
    yield db

    db.delete(famApplication)
    db.commit()


@pytest.fixture(scope="function")
def simpleFOMSubmitterRole_dbSession(
    dbSession_famRoletype, simpleFamApplication_dbSession
):
    db = simpleFamApplication_dbSession
    famApplication: model.FamApplication = (db.query(model.FamApplication).all())[0]

    # add a role record to db
    fomSubmitterRole = model.FamRole(
        **{
            "role_name": FOM_SUBMITTER_ROLE_NAME,
            "role_purpose": "Grant a user access to submit to FOM",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "application_id": famApplication.application_id,
            "role_type_code": famConstants.RoleType.ROLE_TYPE_ABSTRACT,
        }
    )
    db.add(fomSubmitterRole)
    db.commit()
    yield db

    role_db_item = (
        db.query(model.FamRole)
        .filter(model.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)
        .one_or_none()
    )

    if role_db_item:
        db.delete(role_db_item)
        db.commit()


@pytest.fixture(scope="function")
def simpleConcreteRole_dbSession(dbSession_famRoletype, simpleFamApplication_dbSession):
    db = simpleFamApplication_dbSession
    famApplication: model.FamApplication = (db.query(model.FamApplication).all())[0]

    # add a role record to db
    role_name = "Concrete_Test_Role"
    simpleConcreteRole = model.FamRole(
        **{
            "role_name": role_name,
            "role_purpose": "Concrete role for application",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "application_id": famApplication.application_id,
            "role_type_code": famConstants.RoleType.ROLE_TYPE_CONCRETE,
        }
    )
    db.add(simpleConcreteRole)
    db.commit()
    yield db

    role_db_item = (
        db.query(model.FamRole)
        .filter(model.FamRole.role_name == role_name)
        .one_or_none()
    )

    if role_db_item:
        db.delete(role_db_item)
        db.commit()


@pytest.fixture(scope="function")
def clean_up_all_user_role_assignment(dbSession):
    db = dbSession
    yield db

    # Delete fam_user_role_xref
    stmt = text(
        """
        DELETE FROM fam_user_role_xref
        """
    )
    db.execute(stmt)

    # Then role
    stmt = text(
        """
        DELETE FROM fam_role
        """
    )
    db.execute(stmt)

    # Delete user
    stmt = text(
        """
        DELETE FROM fam_user
        """
    )
    db.execute(stmt)
