import os
import logging
import boto3
import json

# re-use the pattern that was used for the db connections for
# the backend

LOGGER = logging.getLogger(__name__)


def get_db_connection_string():
    secret_value = get_aws_db_secret()
    secret_json = json.loads(secret_value["SecretString"])

    username = secret_json.get("username")
    password = secret_json.get("password")

    host = os.environ.get("PG_HOST")
    port = os.environ.get("PG_PORT")
    dbname = os.environ.get("PG_DATABASE")
    db_conn_string = (
        f"user={username} password={password} host={host} "
        + f"port={port} dbname ={dbname}"
    )
    return db_conn_string


def get_aws_db_secret():
    secret_name = os.environ.get("DB_SECRET")
    region_name = "ca-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    return client.get_secret_value(SecretId=secret_name)
