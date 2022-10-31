import os
import logging
import boto3
import json
import dotenv
import re

# re-use the pattern that was used for the db connections for
# the backend

LOGGER = logging.getLogger(__name__)


def get_db_connection_string():
    on_aws = os.environ.get("DB_SECRET")  # This key only presents on aws.
    db_conn_string = getAWSDBString() if on_aws else getLocalDBString()
    return db_conn_string


def getLocalDBString():
    # read the env file if it exists
    envFile = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
    if os.path.exists(envFile):
        dotenv.load_dotenv(envFile)

    # if the env vars are populated they will take precidence, otherwise
    # the values identified here will be used
    username = os.getenv("api_db_username", "fam_proxy_api")  # postgres
    password = os.getenv("api_db_password", "test")
    host = os.getenv("POSTGRES_HOST", "localhost")
    dbname = os.getenv("POSTGRES_DB", "fam")
    port = os.getenv("POSTGRES_PORT", "5432")

    db_conn_string = (
        f"user={username} password={password} host={host} " +
        f"port={port} dbname ={dbname}")

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
        f"user={username} password={password} host={host} " +
        f"port={port} dbname ={dbname}")
    return db_conn_string


def getAWSDBSecret():
    secret_name = os.environ.get("DB_SECRET")
    region_name = "ca-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    return client.get_secret_value(SecretId=secret_name)
