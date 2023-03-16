import os
import logging
import boto3
import json

LOGGER = logging.getLogger(__name__)


def get_env_var(env_var_name):
    if env_var_name not in os.environ:
        raise MissingEnvironmentVariable(env_var_name)
    return os.environ.get(env_var_name)


def is_on_aws():
    return os.environ.get("DB_SECRET") is not None  # This key only presents on aws.


def get_db_string():
    """ retrieves a database connection string for a variety of different
    environments including:
    * local dev with postgres db
    * deployed app using amazon rds

    """
    db_conn_string = get_aws_db_string() if is_on_aws() \
        else get_local_db_string()
    LOGGER.debug(f"Database connection url: {db_conn_string}")
    return db_conn_string


def get_local_db_string():
    username = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    host = os.environ.get("POSTGRES_HOST")
    dbname = os.environ.get("POSTGRES_DB")
    port = os.environ.get("POSTGRES_PORT")
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

    host = get_env_var('PG_HOST')
    port = get_env_var('PG_PORT')
    dbname = get_env_var('PG_DATABASE')
    db_conn_string = (
        f"postgresql+psycopg2://{username}"
        + f":{password}@{host}:{port}/"
        + f"{dbname}"
    )
    return db_conn_string


def get_aws_region():
    env_var = "COGNITO_REGION"
    return get_env_var(env_var)


def get_user_pool_id():
    env_var = "COGNITO_USER_POOL_ID"
    return get_env_var(env_var)


def get_user_pool_domain_name():
    env_var = 'COGNITO_USER_POOL_DOMAIN'
    return get_env_var(env_var)


def get_aws_db_secret():
    secret_name = os.environ.get("DB_SECRET")

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=get_aws_region())

    return client.get_secret_value(SecretId=secret_name)


class MissingEnvironmentVariable(Exception):
    def __init__(self, env_var_name):
        self.message = (
            f'The required environment variable {env_var_name} has not ' +
            'been populated'
        )
        super().__init__(self.message)


if __name__ == '__main__':
    var = get_user_pool_domain_name()
    print(f'var: {var}')


def get_root_path():
    root_path = ""

    api_gateway_stage_name = os.environ.get("API_GATEWAY_STAGE_NAME")
    if api_gateway_stage_name:
        root_path = f"/{api_gateway_stage_name}"

    return root_path


_client_id = None


def get_oidc_client_id():

    # Outside of AWS, you can set COGNITO_CLIENT_ID
    # Inside AWS, you have to get this value from an AWS Secret

    global _client_id

    if not _client_id:
        client_id_secret_name = os.environ.get("COGNITO_CLIENT_ID_SECRET")
        if client_id_secret_name:
            session = boto3.session.Session()
            client = session.client(service_name="secretsmanager",
                                    region_name=get_aws_region())
            secret_value = client.get_secret_value(SecretId=client_id_secret_name)
            LOGGER.info(f"Secret retrieved -- value: [{secret_value}]")
            _client_id = secret_value["SecretString"]

    if not _client_id:
        _client_id = os.environ.get("COGNITO_CLIENT_ID")

    return _client_id


def get_allow_origins():
    allow_origins = [get_env_var("ALLOW_ORIGIN")] if is_on_aws() else ["*"]
    LOGGER.info(f"allow_origins -- {allow_origins}")
    return allow_origins
