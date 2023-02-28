import pytest
import logging
import testcontainers.compose
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


LOGGER = logging.getLogger(__name__)
COMPOSE_PATH = os.path.dirname(__file__)  # the folder contains test docker-compose.yml


@pytest.fixture(scope="module")
def dbPgContainer():
    compose = testcontainers.compose.DockerCompose(COMPOSE_PATH)
    return compose


@pytest.fixture(scope="module")
def dbPgEngine() -> Engine:
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/fam")
    return engine


@pytest.fixture(scope="function")
def dbPgSession(dbPgEngine: Engine) -> sessionmaker:
    _session_local = sessionmaker(bind=dbPgEngine)
    return _session_local()
