import logging

import api.app.models.model as model
import api.app.schemas as schemas
import pytest
from sqlalchemy.orm import session
import api.app.constants as famConstants

LOGGER = logging.getLogger(__name__)

FOM_SUBMITTER_ROLE_NAME = "FOM_Submitter"

@pytest.fixture(scope="function")
def simpleUserRoleData() -> dict:
    userRoleData = {
        "user_name": "Test User",
        "user_type": famConstants.UserType.BCEID,
        "role_id": 2,
        "client_number_id": 1001  # Forest Client id
    }
    yield userRoleData


@pytest.fixture(scope="function")
def simpleUserRoleRequest(simpleUserRoleData) -> schemas.FamUserRoleAssignmentCreate:
    famUserRoleRequest = schemas.FamUserRoleAssignmentCreate(**simpleUserRoleData)
    yield famUserRoleRequest


@pytest.fixture(scope="function")
def deleteAllUserRoleAssignment(
    dbSession: session.Session, deleteAllUsers, deleteAllRoles
) -> None:
    """Cleans up all fam_user_role_xref from the database"""
    yield
    # db = dbSession
    # famUserRoles = db.query(model.FamUserRoleXref).all()
    # for famUserRole in famUserRoles:
    #     db.delete(famUserRole)
    # db.commit()


@pytest.fixture(scope="function")
def simpleFOMSubmitterRole_dbSession(
    dbSession: session.Session,
):
    db = dbSession
    # add a role record to db
    newRole = model.FamRole(
        **{
            "role_name": FOM_SUBMITTER_ROLE_NAME,
            "role_purpose": "Grant a user access to submit to FOM",
            "create_user": famConstants.FAM_PROXY_API_USER
        }
    )
    db.add(newRole)
    db.commit()
    yield db
