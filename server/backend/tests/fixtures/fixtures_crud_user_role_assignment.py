import logging

import api.app.constants as famConstants
import api.app.models.model as model
import api.app.schemas as schemas
import pytest
from sqlalchemy.orm import session

LOGGER = logging.getLogger(__name__)

FOM_SUBMITTER_ROLE_NAME = "FOM_Submitter"


@pytest.fixture(scope="function")
def simpleUserRoleData() -> dict:
    userRoleData = {
        "user_name": "Test User",
        "user_type": famConstants.UserType.BCEID,
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
    simpleFOMSubmitterRole_dbSession: session.Session
):
    db = simpleFOMSubmitterRole_dbSession
    fam_role: model.FamRole = (db.query(model.FamRole).all())[0]

    # add dummy user
    fam_user = model.FamUser(
        **{
            "user_type": famConstants.UserType.IDIR,
            "user_name": famConstants.DUMMY_FOREST_CLIENT_NAME,
            "create_user": famConstants.FAM_PROXY_API_USER
        }
    )
    db.add(fam_user)
    db.flush()

    # add user/role assignment
    user_role_assignment = model.FamUserRoleXref(
        **{
            "user_id": fam_user.user_id,
            "role_id": fam_role.role_id,
            "create_user": famConstants.FAM_PROXY_API_USER
        }
    )
    db.add(user_role_assignment)
    db.commit()
    yield db

    db.delete(user_role_assignment)
    db.delete(fam_user)
    db.commit()


@pytest.fixture(scope="function")
def simpleFOMSubmitterRole_dbSession(
    dbSession_famRoletype: session.Session,
):
    db = dbSession_famRoletype

    # add an application to db
    famApplication = model.FamApplication(
        **{
            "application_name": "FOM",
            "application_description": "Forest Operations Map",
            "create_user": famConstants.FAM_PROXY_API_USER,
        }
    )
    db.add(famApplication)
    db.flush()

    # add a role record to db
    fomSubmitterRole = model.FamRole(
        **{
            "role_name": FOM_SUBMITTER_ROLE_NAME,
            "role_purpose": "Grant a user access to submit to FOM",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "application_id": famApplication.application_id,
            "role_type_code": model.FamRoleType.ROLE_TYPE_ABSTRACT,
        }
    )
    db.add(fomSubmitterRole)
    db.commit()
    yield db

    db.delete(fomSubmitterRole)
    db.delete(famApplication)
    db.commit()
