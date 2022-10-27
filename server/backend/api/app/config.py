import os
import logging
import boto3
import json

LOGGER = logging.getLogger(__name__)

# APP_ENV = os.getenv("APP_ENV", "dev")


def getDBString():
    on_aws = os.environ.get("DB_SECRET")  # This key only presents on aws.
    db_conn_string = getAWSDBString() if on_aws else getLocalDBString()
    LOGGER.debug(f"Database connection url: {db_conn_string}")
    return db_conn_string


def getLocalDBString():
    username = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "test")
    host = os.getenv("POSTGRES_HOST", "localhost")
    dbname = os.getenv("POSTGRES_DB", "fam")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_conn_string: str

    # if the POSTGRESQL_USER env var is populated then use a postgres
    if "POSTGRES_USER" in os.environ:
        db_conn_string = (
            f"postgresql+psycopg2://{username}" +
            f":{password}@{host}:{port}/" +
            f"{dbname}"
        )
    else:
        # force default sqllite database if not POSTGRES vars not defined
        curdir = os.path.dirname(__file__)
        databaseFile = os.path.join(curdir, "..", "fam.db")
        LOGGER.debug(f"databaseFile: {databaseFile}")
        db_conn_string = f"sqlite:///{databaseFile}"

    return db_conn_string


def getAWSDBString():
    secret_value = getAWSDBSecret()
    secret_json = json.loads(secret_value["SecretString"])

    username = secret_json.get("username")
    password = secret_json.get("password")

    host = os.environ.get("PG_HOST")
    port = os.environ.get("PG_PORT")
    dbname = os.environ.get("PG_DATABASE")
    db_conn_string = (
        f"postgresql+psycopg2://{username}" +
        f":{password}@{host}:{port}/" +
        f"{dbname}"
    )
    return db_conn_string


def getAWSDBSecret():
    secret_name = os.environ.get("DB_SECRET")
    region_name = "ca-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    return client.get_secret_value(SecretId=secret_name)
