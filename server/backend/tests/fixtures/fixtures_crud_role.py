import datetime
import logging
from typing import Dict, List, Union

import api.app.models.model as model
import api.app.schemas as schemas
import pytest
import sqlalchemy.exc
from sqlalchemy.orm import session

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def dbSession_famRoles_withSimpleData(dbSession_famRoletype, simpleRoleData):
    db = dbSession_famRoletype

    # add a record to the database
    newRole = model.FamRole(**simpleRoleData)
    db.add(newRole)
    db.commit()
    yield db  # use the session in tests.
    LOGGER.debug(f"newRole: {newRole}")
    db.delete(newRole)
    db.commit()


@pytest.fixture(scope="function")
def dbSession_famRoletype(dbSession, abstractRoleTypeRecord, concreteRoleTypeRecord):
    db = dbSession
    roleTypeModel_abstract = model.FamRoleType(**abstractRoleTypeRecord)
    db.add(roleTypeModel_abstract)
    roleTypeModel_concrete = model.FamRoleType(**concreteRoleTypeRecord)
    db.add(roleTypeModel_concrete)
    db.commit()
    yield db  # use the session in tests.

    try:
        db.delete(roleTypeModel_abstract)
    except sqlalchemy.exc.InvalidRequestError as e:
        LOGGER.error(f"wasn't committed: {e}")

    try:
        db.delete(roleTypeModel_concrete)
    except sqlalchemy.exc.InvalidRequestError as e:
        LOGGER.debug(f"wasn't committed: {e}")


@pytest.fixture(scope="function")
def concreteRoleTypeRecord() -> Dict[
    str, Union[str, datetime.datetime]
]:
    roleType = {
        "role_type_code": model.FamRoleType.ROLE_TYPE_CONCRETE,
        "description": "describe describe describe",
        "effective_date": datetime.datetime.now(),
    }
    yield roleType


@pytest.fixture(scope="function")
def abstractRoleTypeRecord() -> Dict[str, Union[datetime.datetime,
                                                str]]:
    roleType = {
        "role_type_code": model.FamRoleType.ROLE_TYPE_ABSTRACT,
        "description": "describe describe describe",
        "effective_date": datetime.datetime.now(),
    }
    yield roleType


@pytest.fixture(scope="function")
def simpleRoleData_asPydantic(simpleRoleData) -> schemas.FamRoleCreate:
    famRoleAsPydantic = schemas.FamRoleCreate(**simpleRoleData)
    yield famRoleAsPydantic


@pytest.fixture(scope="function")
def simpleRoleData() -> Dict[str, str]:
    roleData = {
        "role_name": "FAM_ADMIN",
        "role_purpose": "FAM Admin",
        "create_user": "John Doe",
        "role_type_code": model.FamRoleType.ROLE_TYPE_CONCRETE,
    }
    yield roleData


@pytest.fixture(scope="function")
def simpleRoleData2() -> Dict[str, str]:
    roleData = {
        "role_name": "FAM_TEST",
        "role_purpose": "FAM Testing",
        "create_user": "Patrick Roy",
        "role_type_code": model.FamRoleType.ROLE_TYPE_CONCRETE,
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


@pytest.fixture(scope="function")
def deleteAllRoleTypes(dbSession: session.Session) -> None:
    """cleans up all role types from the database"""
    LOGGER.debug(f"dbsession type: {type(dbSession)}")
    yield

    db = dbSession
    famRoles = db.query(model.FamRole).all()
    for famRole in famRoles:
        db.delete(famRole)

    db = dbSession
    famRoleTypes = db.query(model.FamRoleType).all()
    for famRoleType in famRoleTypes:
        db.delete(famRoleType)
    db.commit()
