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

import logging
import sys
from typing import Any, Generator

import api.app.dependencies as dependencies
import api.app.models.model as model
import pytest
from api.app.database import Base
from api.app.main import app
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker

# global placeholder to be populated by fixtures for database test
# sessions, required to override the get_db method.
testSession = None

LOGGER = logging.getLogger(__name__)

# crud code is useful for setting up the router tests, so making
# it available for use globally
pytest_plugins = [
    "fixtures.fixtures_crud_application",
    "fixtures.fixtures_router_application",
    "fixtures.fixtures_crud_user",
    "fixtures.fixtures_crud_role"
]


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


# This @event is important. By default FOREIGN KEY constraints have no effect on the operation of the table from SQLite.
# It (FOREIGN KEY) only works when emitting CREATE statements for tables.
# Reference: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#foreign-key-support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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


def override_get_db():
    try:
        db = testSession()
        yield db
    finally:
        db.close()
