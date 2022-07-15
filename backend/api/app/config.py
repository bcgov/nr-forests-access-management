import os
import logging

APP_ENV = os.getenv("APP_ENV", "dev")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "fam")
POSTGRES_DB_TEST = os.getenv("POSTGRES_DB_TEST", "fam_test")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

LOGGER = logging.getLogger(__name__)


def getDBString():
    SQLALCHEMY_DATABASE_URL = os.getenv("DB_CONN")
    if not SQLALCHEMY_DATABASE_URL:
        # force default sqllite database if not POSTGRES vars not defined
        curdir = os.path.dirname(__file__)
        databaseFile = os.path.join(curdir, "..", "fam.db")
        LOGGER.debug(f"databaseFile: {databaseFile}")
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{databaseFile}"
        LOGGER.debug(f"SQLALCHEMY_DATABASE_URL: {SQLALCHEMY_DATABASE_URL}")

    # if the POSTGRESQL_USER env var is populated then use a postgres
    if "POSTGRES_USER" in os.environ:
        SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}" + \
            f":{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/" + \
            f"{POSTGRES_DB}"
        LOGGER.debug(f"db conn str: {SQLALCHEMY_DATABASE_URL}")
    return SQLALCHEMY_DATABASE_URL
