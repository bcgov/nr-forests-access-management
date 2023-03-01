import pytest
import time
import logging
import testcontainers.compose
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Crypto.PublicKey import RSA
from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import api.app.jwt_validation as jwt_validation
from api.app.main import app


LOGGER = logging.getLogger(__name__)
# the folder contains test docker-compose.yml, ours in the root directory
COMPOSE_PATH = os.path.join(os.path.dirname(__file__), '../../../')


@pytest.fixture(scope="session")
def dbPgContainer():
    compose = testcontainers.compose.DockerCompose(COMPOSE_PATH)
    compose.start()
    time.sleep(5)  # wait db migration script to run
    yield compose
    compose.stop()


@pytest.fixture(scope="session")
def dbPgEngine() -> Engine:
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/fam")
    return engine


@pytest.fixture(scope="module")
def dbPgConnection(dbPgContainer, dbPgEngine: Engine):
    _session_local = sessionmaker(bind=dbPgEngine)
    db = _session_local()
    yield db
    db.close()


@pytest.fixture(scope="function")
def dbPgSession(dbPgConnection: sessionmaker) -> sessionmaker:
    return dbPgConnection


@pytest.fixture(scope="function")
def test_client_fixture() -> TestClient:
    """returns a requests object of the current app,
    with the objects defined in the model created in it.

    :rtype: starlette.testclient
    """
    client = TestClient(app)
    return client


@pytest.fixture(scope="function")
def test_rsa_key():

    new_key = RSA.generate(2048)
    global public_rsa_key
    public_rsa_key = new_key.publickey().exportKey("PEM")

    app.dependency_overrides[jwt_validation.get_rsa_key_method] = \
        override_get_rsa_key_method

    return new_key.exportKey("PEM")


def override_get_rsa_key_method():
    return override_get_rsa_key


def override_get_rsa_key(kid):
    global public_rsa_key
    return public_rsa_key
