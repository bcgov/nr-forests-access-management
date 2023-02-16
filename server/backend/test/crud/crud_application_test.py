import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from api.app import config
from api.app.crud import crud_application

import testcontainers.compose
import time
import sqlalchemy
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = config.get_db_string()
COMPOSE_PATH = "./test"  # the folder containing docker-compose.yml

# # postgresql+psycopg2://postgres:postgres@localhost:5432/fam


def get_db_conn():
    """function returning the DB psycopg2 connection."""
    ...
    # return sqlalchemy.create_engine(
    #     "postgresql+psycopg2://postgres:postgres@localhost:5432/fam"
    # )
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)
    _session_local = sessionmaker(bind=engine)

    return _session_local()


def test_db():
    compose = testcontainers.compose.DockerCompose(COMPOSE_PATH)
    compose.start()
    time.sleep(10)  # wait db migration script to run
    db = get_db_conn()
    query_data = crud_application.get_applications(db)
    print(123, query_data)
    assert len(query_data) == 4
    db.close()
    compose.stop()
