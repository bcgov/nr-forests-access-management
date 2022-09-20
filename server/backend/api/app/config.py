import os
import logging
import boto3
import json

LOGGER = logging.getLogger(__name__)

"""
TODO: Need some discission to:
1. synchronize environment variables below (local envs / aws envs).
2. refactor getDBString() function.
"""

on_aws = os.environ.get('DB_SECRET')  # This key only presents on aws.

APP_ENV = os.getenv("APP_ENV", "dev")  # TODO: ? What other APP_ENV does the deployment have ?
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "fam")
POSTGRES_DB_TEST = os.getenv("POSTGRES_DB_TEST", "fam_test")  # TODO: Is this being used or intention?
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")


def getDBString():

    secret_json = {}
    if on_aws:
        secret_value = get_secret()
        secret_json = json.loads(secret_value['SecretString'])

    username = secret_json.get('username', POSTGRES_USER)
    password = secret_json.get('password', POSTGRES_PASSWORD)

    host = os.environ.get('PG_HOST', POSTGRES_HOST)
    port = os.environ.get('PG_PORT', POSTGRES_PORT)
    dbname = os.environ.get('PG_DATABASE', POSTGRES_DB)

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
        SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{username}" + \
            f":{password}@{host}:{port}/" + \
            f"{dbname}"

    LOGGER.debug(f"db conn str: {SQLALCHEMY_DATABASE_URL}")
    return SQLALCHEMY_DATABASE_URL


def get_secret():

    secret_name = os.environ.get('DB_SECRET')
    region_name = "ca-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    return client.get_secret_value(SecretId=secret_name)
