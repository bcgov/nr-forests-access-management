import logging
import os
import sys
import time

import jwt_utils as jwt_utils
import pytest
import testcontainers.compose
from Crypto.PublicKey import RSA
from fastapi.testclient import TestClient
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session, sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import api.app.database as database
import api.app.jwt_validation as jwt_validation
from api.app.main import app

LOGGER = logging.getLogger(__name__)
# the folder contains test docker-compose.yml, ours in the root directory
COMPOSE_PATH = os.path.join(os.path.dirname(__file__), '../../../')


@pytest.fixture(scope="session")
def db_pg_container():
    compose = testcontainers.compose.DockerCompose(COMPOSE_PATH)
    compose.start()
    time.sleep(5)  # wait db migration script to run
    yield compose
    compose.stop()


@pytest.fixture(scope="session")
def db_pg_engine() -> Engine:
    engine = create_engine("postgresql+psycopg2://" +
                           f"{os.environ.get('POSTGRES_USER')}:" +
                           f"{os.environ.get('POSTGRES_PASSWORD')}@" +
                           f"{os.environ.get('POSTGRES_HOST')}:"
                           f"{os.environ.get('POSTGRES_PORT')}/"
                           f"{os.environ.get('POSTGRES_DB')}")
    return engine


@pytest.fixture(scope="module")
def db_pg_connection(db_pg_container, db_pg_engine: Engine):
    _session_local = sessionmaker(bind=db_pg_engine)
    db = _session_local()
    yield db
    db.close()


@pytest.fixture(scope="function")
def db_pg_session(db_pg_connection: Session) -> Session:
    return db_pg_connection


@pytest.fixture(scope="function")
def test_client_fixture_unit() -> TestClient:

    app.dependency_overrides[database.get_db] = \
        lambda: UnifiedAlchemyMagicMock(data=[])

    return TestClient(app)


@pytest.fixture(scope="function")
def test_client_fixture() -> TestClient:
    """returns a requests object of the current app,
    with the objects defined in the model created in it.

    :rtype: starlette.testclient
    """
    # reset to default database which points to postgres container
    app.dependency_overrides[database.get_db] = database.get_db
    return TestClient(app)


@pytest.fixture(scope="function")
def test_rsa_key():

    new_key = RSA.generate(2048)
    global public_rsa_key
    public_rsa_key = new_key.publickey().exportKey("PEM")

    app.dependency_overrides[jwt_validation.get_rsa_key_method] = \
        override_get_rsa_key_method

    return new_key.exportKey("PEM")


@pytest.fixture(scope="function")
def test_rsa_key_missing():

    new_key = RSA.generate(2048)
    global public_rsa_key
    public_rsa_key = new_key.publickey().exportKey("PEM")

    app.dependency_overrides[jwt_validation.get_rsa_key_method] = \
        override_get_rsa_key_method_none

    return new_key.exportKey("PEM")


def override_get_rsa_key_method():
    return override_get_rsa_key


def override_get_rsa_key(kid):
    global public_rsa_key
    return public_rsa_key


def override_get_rsa_key_method_none():
    return override_get_rsa_key_none


def override_get_rsa_key_none(kid):
    return None
