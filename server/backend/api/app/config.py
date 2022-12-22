import os
import logging
import boto3
import json

LOGGER = logging.getLogger(__name__)


def get_db_string():
    on_aws = os.environ.get("DB_SECRET")  # This key only presents on aws.
    db_conn_string = get_aws_db_string() if on_aws \
        else get_local_db_string()
    LOGGER.debug(f"Database connection url: {db_conn_string}")
    return db_conn_string


def get_local_db_string():
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    dbname = os.getenv("POSTGRES_DB")
    port = os.getenv("POSTGRES_PORT")
    LOGGER.debug(f"api db user: {username}")

    db_conn_string = (
        f"postgresql+psycopg2://{username}"
        + f":{password}@{host}:{port}/"
        + f"{dbname}"
        )

    return db_conn_string


def get_aws_db_string():
    secret_value = get_aws_db_secret()
    secret_json = json.loads(secret_value["SecretString"])

    username = secret_json.get("username")
    password = secret_json.get("password")

    host = os.environ.get("PG_HOST")
    port = os.environ.get("PG_PORT")
    dbname = os.environ.get("PG_DATABASE")
    db_conn_string = (
        f"postgresql+psycopg2://{username}"
        + f":{password}@{host}:{port}/"
        + f"{dbname}"
    )
    return db_conn_string


def get_aws_region():
    return os.environ.get("AWS_REGION")


def get_user_pool_id():
    return os.environ.get("AWS_USER_POOL_ID")


def get_oidc_client_id():
    return os.environ.get("OIDC_CLIENT_ID")


def get_user_pool_domain_name():
    return os.environ.get("AWS_USER_POOL_DOMAIN")


def get_aws_db_secret():
    secret_name = os.environ.get("DB_SECRET")

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=get_aws_region())

    return client.get_secret_value(SecretId=secret_name)
