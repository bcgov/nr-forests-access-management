""" setup for testing

based loosely on this:
https://fastapi.tiangolo.com/advanced/testing-database/

:return: _description_
:rtype: _type_
:yield: _description_
:rtype: _type_
"""
# flake8: ignore=F402

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.append(os.path.dirname(__file__))

import datetime
import logging
import sys
import uuid
from typing import Any, Generator, TypedDict

import api.app.crud as crud
import api.app.dependencies as dependencies
import api.app.models.model as model
import api.app.schemas as schemas
import pytest
from api.app.database import Base
from api.app.main import app
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import session, sessionmaker

# global placeholder to be populated by fixtures for database test
# sessions, required to override the get_db method.
testSession = None

LOGGER = logging.getLogger(__name__)

# crud code is useful for setting up the router tests, so making
# it available for use globally
pytest_plugins = [
    "fixtures.fixtures_crud_application",
    "fixtures.fixtures_router_application",
]


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
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=dbEngine)
    LOGGER.debug(f"session type: {type(SessionTesting)}")
    yield SessionTesting


@pytest.fixture(scope="module")
def dbEngine() -> Engine:
    # should re-create the database every time the tests are run, the following
    # line ensure database that maybe hanging around as a result of a failed
    # test is deleted
    if os.path.exists("./test_db.db"):
        LOGGER.debug("remove the database: ./test_db.db'")
        os.remove("./test_db.db")

    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
    LOGGER.debug(f"SQL Alchemy URL: {SQLALCHEMY_DATABASE_URL}")
    execution_options = {"schema_translate_map": {"app_fam": None}}

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        execution_options=execution_options,
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
def dbSession(dbEngine, sessionObjects) -> Generator[sessionObjects, Any, None]:

    connection = dbEngine.connect()
    # transaction = connection.begin()
    session = sessionObjects(bind=connection)
    yield session  # use the session in tests.

    session.close()
    # transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def dbSession_famUsers_withdata(
    dbSession, testUserData3, testGroupData, userGroupXrefData
):
    """to add a user need to satisfy the integrity constraints:

    1. create the group
    2. retrieve the group id
    3.

    :param dbSession: _description_
    :type dbSession: _type_
    :param testUserData: _description_
    :type testUserData: _type_
    :param add_group: _description_
    :type add_group: _type_
    :yield: _description_
    :rtype: _type_
    """
    # the following link goes over working with related/associated tables
    # https://www.pythoncentral.io/sqlalchemy-association-tables/

    db = dbSession
    # trying to add to user without violating the integrity constraint
    # group was populated with a record by the add_group fixture.
    newUser = model.FamUser(**testUserData3)
    groupSchema = model.FamGroup(**testGroupData)

    userGroupXrefData["group"] = groupSchema
    userGroupXrefData["user"] = newUser

    xrefTable = model.FamUserGroupXref(**userGroupXrefData)
    db.add(xrefTable)
    db.commit()

    yield db

    db.delete(xrefTable)
    db.delete(groupSchema)
    db.delete(newUser)

    db.commit()


@pytest.fixture(scope="function")
def userGroupXrefData():
    nowdatetime = datetime.datetime.now()
    xrefData = {
        "create_user": "serg",
        "create_date": nowdatetime,
        "update_user": "ron",
        "update_date": nowdatetime,
    }
    yield xrefData


@pytest.fixture(scope="function")
def add_group(dbSession, testGroupData):
    db = dbSession
    groupSchema = schemas.FamGroupPost(**testGroupData)

    crud.createFamGroup(famGroup=groupSchema, db=db)
    yield db

    db.delete(testGroupData)
    db.commit()


@pytest.fixture(scope="function")
def testGroupData():
    testGroupData = {
        "group_id": 99,
        "group_name": "test group",
        "purpose": "testing",
        "create_user": "Brian Trotier",
        "create_date": datetime.datetime.now(),
        "parent_group_id": 1,
        "client_number_id": 1,
        "update_user": "Brian Trotier",
        "update_date": datetime.datetime.now(),
    }
    return testGroupData


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
    """Cleans up all users from the database after the test has been run

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
def testUserData3() -> FamUserTD:
    userData = {
        "user_id": 33,
        "user_type": "a",
        "cognito_user_id": "zzff",
        "user_name": "Billy Smith",
        "user_guid": str(uuid.uuid4()),
        "create_user": "Al Arbour",
        "create_date": datetime.datetime.now(),
        "update_user": "Al Arbour",
        "update_date": datetime.datetime.now(),
    }
    yield userData


def override_get_db():
    try:
        db = testSession()
        yield db
    finally:
        db.close()
