from typing import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from fastapi.testclient import TestClient
import os

from api.app.database import Base
import api.app.routers.fam_router as fam_router
import api.app.models.model as model


import pytest


@pytest.fixture
def test_fixture():
    var = 20
    yield var

@pytest.fixture(scope="module")
def dbEngine():
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    model.Base.metadata.create_all(bind=engine)
    yield engine

@pytest.fixture(scope="module")
def sessionObjects(dbEngine):
    # Use connect_args parameter only with sqlite
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=dbEngine)
    yield SessionTesting
    if os.path.exists('./test_db.db'):
        os.remove('./test_db.db')

@pytest.fixture(scope="function")
def app(sessionObjects, dbEngine) -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(dbEngine)  # Create the tables.
    _app = start_application()
    yield _app
    Base.metadata.drop_all(dbEngine)

@pytest.fixture(scope="function")
def dbSession(app: FastAPI, dbEngine, sessionObjects) -> Generator[sessionObjects, Any, None]:

    connection = dbEngine.connect()
    transaction = connection.begin()
    session = sessionObjects(bind=connection)
    yield session  # use the session in tests.

    session.close()
    transaction.rollback()
    connection.close()

def start_application():
    # not a fixture
    app = FastAPI()
    app.include_router(fam_router.router)
    return app