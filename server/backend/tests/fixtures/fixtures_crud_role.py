import logging
from typing import List

import api.app.models.model as model
import api.app.schemas as schemas
import pytest
from sqlalchemy.orm import session

LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def dbSession_famRoles_withSimpleData(dbSession, simpleRoleData):
    db = dbSession
    # add a record to the database
    newRole = model.FamRole(**simpleRoleData)
    db.add(newRole)
    db.commit()
    yield db  # use the session in tests.

    db.delete(newRole)
    db.commit()


@pytest.fixture(scope="function")
def simpleRoleData_asPydantic(simpleRoleData) -> schemas.FamRoleCreate:
    famRoleAsPydantic = schemas.FamRoleCreate(**simpleRoleData)
    yield famRoleAsPydantic


@pytest.fixture(scope="function")
def simpleRoleData() -> dict:
    roleData = {
        "role_name": "FAM_ADMIN",
        "role_purpose": "FAM Admin",
        "create_user": "John Doe"
    }
    yield roleData


@pytest.fixture(scope="function")
def deleteAllRoles(dbSession: session.Session) -> None:
    """Cleans up all roles from the database after the test has been run

    :param dbSession: mocked up database session
    :type dbSession: sqlalchemy.orm.session.Session
    """
    yield
    db = dbSession
    famRoles: List[model.FamRole] = db.query(model.FamRole).all()
    for famRole in famRoles:
        db.delete(famRole)
    db.commit()
