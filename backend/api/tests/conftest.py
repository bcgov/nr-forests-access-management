""" setup for testing

based loosely on this:
https://fastapi.tiangolo.com/advanced/testing-database/

:return: _description_
:rtype: _type_
:yield: _description_
:rtype: _type_
"""

import datetime
import logging
import os
import uuid
from typing import Any, Generator, TypedDict

import api.app.dependencies as dependencies
import api.app.models.model as model
import api.app.schemas as schemas
import pytest
from api.app.database import Base
from api.app.main import app
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session

from sqlalchemy.engine.base import Engine

# global placeholder to be populated by fixtures for database test
# sessions, required to override the get_db method.
testSession = None

LOGGER = logging.getLogger(__name__)


class FamUserTD(TypedDict):
    # cludge... ideally this type should be derived from the
    # pydantic model schema.FamUser
    user_type: str
    cognito_user_id: str
    user_name: str
    user_guid: str
    create_user: str
    create_date: datetime.datetime
    update_user: str
    update_date: datetime.datetime

@pytest.fixture(scope="function")
def getApp(sessionObjects, dbEngine: Engine) -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(dbEngine)  # Create the tables.
    global testSession
    testSession = sessionObjects
    app.dependency_overrides[dependencies.get_db] = override_get_db
    yield app


@pytest.fixture(scope="function")
def testClient_fixture(getApp: FastAPI) -> TestClient:
    """returns a requests object of the current app backed by a test
    database, with the objects defined in the model created in it.

    :param getApp: the FastAPI app
    :type getApp: FastAPI
    :yield: a requests client backed by the app in this directory.
    :rtype: starlette.testclient
    """
    client = TestClient(getApp)
    yield client


@pytest.fixture(scope="module")
def sessionObjects(dbEngine: Engine) -> sessionmaker:
    # Use connect_args parameter only with sqlite
    SessionTesting = sessionmaker(autocommit=False,
                                  autoflush=False,
                                  bind=dbEngine)
    LOGGER.debug(f"session type: {type(SessionTesting)}")
    yield SessionTesting


@pytest.fixture(scope="module")
def dbEngine() -> Engine:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
    LOGGER.debug(f"SQL Alchemy URL: {SQLALCHEMY_DATABASE_URL}")

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    model.Base.metadata.create_all(bind=engine)
    LOGGER.debug(f"engine type: {type(engine)}")
    yield engine

    # dropping all objects in the test database and...
    # delete the test database
    model.Base.metadata.drop_all(engine)
    if os.path.exists("./test_db.db"):
        LOGGER.debug("remove the database: ./test_db.db'")
        os.remove("./test_db.db")



@pytest.fixture(scope="function")
def dbSession(dbEngine, sessionObjects) -> Generator[sessionObjects,
                                                     Any, None]:

    connection = dbEngine.connect()
    # transaction = connection.begin()
    session = sessionObjects(bind=connection)
    yield session  # use the session in tests.

    session.close()
    # transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def dbSession_famUsers_withdata(dbSession, testUserData):
    db = dbSession
    # add a record to the database
    newUser = model.FamUser(**testUserData)
    db.add(newUser)
    db.commit()
    yield db  # use the session in tests.

    db.delete(newUser)
    db.commit()


@pytest.fixture(scope="function")
def testUserData_asPydantic(testUserData) -> schemas.FamUser:
    famUserAsPydantic = schemas.FamUser(**testUserData)
    yield famUserAsPydantic


@pytest.fixture(scope="function")
def testUserData2_asPydantic(testUserData2) -> schemas.FamUser:
    famUserAsPydantic2 = schemas.FamUser(**testUserData2)
    yield famUserAsPydantic2


@pytest.fixture(scope="function")
def deleteAllUsers(dbSession: session.Session) -> None:
    """ Cleans up all users from the database after the test has been run

    :param dbSession: mocked up database session
    :type dbSession: sqlalchemy.orm.session.Session
    """
    LOGGER.debug(f"dbsession type: {type(dbSession)}")
    yield
    db = dbSession
    famUsers = db.query(model.FamUser).all()
    for famUser in famUsers:
        db.delete(famUser)
    db.commit()


@pytest.fixture(scope="function")
def testUserData() -> dict:

    userData = {
        "user_type": "a",
        "cognito_user_id": "22ftw",
        "user_name": "Mike Bossy",
        "user_guid": str(uuid.uuid4()),
        "create_user": "Al Arbour",
        "create_date": datetime.datetime.now(),
        "update_user": "Al Arbour",
        "update_date": datetime.datetime.now(),
    }
    yield userData


@pytest.fixture(scope="function")
def testUserData2() -> FamUserTD:
    userData = {
        "user_type": "a",
        "cognito_user_id": "22dfs",
        "user_name": "Dennis Potvin",
        "user_guid": str(uuid.uuid4()),
        "create_user": "Al Arbour",
        "create_date": datetime.datetime.now(),
        "update_user": "Al Arbour",
        "update_date": datetime.datetime.now(),
    }
    yield userData

@pytest.fixture(scope="function")
def dbSession_famRoles_withdata(dbSession, testRoleData):
    db = dbSession
    # add a record to the database
    newRole = model.FamRole(**testRoleData)
    db.add(newRole)
    db.commit()
    yield db  # use the session in tests.

    db.delete(newRole)
    db.commit()


@pytest.fixture(scope="function")
def addApplication(dbSession, testApplicationData):
    """ This test is going to add and application record to the database and
    then when the test is torn down it will remove that record.

    Args:
        dbSession (_type_): _description_
        testApplicationData (_type_): _description_
    """
    db = dbSession
    newApp = model.FamApplication(**testApplicationData)
    db.add(newApp)
    db.commit()
    yield db  # use the session in tests.

    db.delete(newApp)
    db.commit()

@pytest.fixture(scope="function")
def testApplicationData(dbSession):
    appData = {
        "application_name" : 'testapp',
        "applicationdescription": "test description"

    }
    yield appData



@pytest.fixture(scope="function")
def testRoleData_asPydantic(testRoleData) -> schemas.FamRole:
    famRoleAsPydantic = schemas.FamRole(**testRoleData)
    yield famRoleAsPydantic

@pytest.fixture(scope="function")
def testRoleData() -> dict:
    roleData = {
        "role_id": "23",
        "role_name": "admin",
        "role_purpose": "admin",
        "parent_role_id": "3",
        "client_number_id": "2021",
        "create_user": "John Doe",
        "update_user": "John Doe",
    }
    yield roleData

def override_get_db():
    try:
        db = testSession()
        yield db
    finally:
        db.close()




