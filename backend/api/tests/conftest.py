""" setup for testing

based loosely on this:
https://fastapi.tiangolo.com/advanced/testing-database/

:return: _description_
:rtype: _type_
:yield: _description_
:rtype: _type_
"""

import logging
import os
import uuid
from typing import Any, Generator

import api.app.dependencies as dependencies
import api.app.models.model as model
import pytest
from api.app.database import Base
from api.app.main import app
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# global placeholder to be populated by fixtures for database test
# sessions, required to override the get_db method.
testSession = None

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def getApp(sessionObjects, dbEngine) -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(dbEngine)  # Create the tables.
    global testSession
    testSession = sessionObjects
    app.dependency_overrides[dependencies.get_db] = override_get_db
    yield app


@pytest.fixture(scope="function")
def testClient_fixture(getApp: FastAPI):
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
def sessionObjects(dbEngine):
    # Use connect_args parameter only with sqlite
    SessionTesting = sessionmaker(autocommit=False, autoflush=False,
                                  bind=dbEngine)
    yield SessionTesting
    if os.path.exists("./test_db.db"):
        LOGGER.debug("remove the database: ./test_db.db'")
        # TODO: once get working uncomment below
        # os.remove('./test_db.db')


@pytest.fixture(scope="module")
def dbEngine():
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
    LOGGER.debug(f"SQL Alchemy URL: {SQLALCHEMY_DATABASE_URL}")

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    model.Base.metadata.create_all(bind=engine)

    yield engine

    # TODO: uncomment once working
    # model.Base.metadata.drop_all(dbEngine)


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
def testUserData() -> dict:

    userData = {
        "user_type": "a",
        "cognito_user_id": "xyz123",
        "user_name": "Bill",
        "user_guid": str(uuid.uuid4()),
        "create_user": "Bill",
        "create_date": "2022-07-13T21:24:15.385Z",
        "update_user": "Bill",
        "update_date": "2022-07-13T21:24:15.385Z",
    }
    yield userData


def override_get_db():
    try:
        db = testSession()
        yield db
    finally:
        db.close()
