import json
import logging
import os

import boto3
from api.app.constants import ApiInstanceEnv, AppEnv, AwsTargetEnv

LOGGER = logging.getLogger(__name__)


def get_env_var(env_var_name):
    if env_var_name not in os.environ:
        raise MissingEnvironmentVariable(env_var_name)
    return os.environ.get(env_var_name)


def is_on_aws():
    return os.environ.get("DB_SECRET") is not None  # This key only presents on aws.


def get_aws_target_env():
    # target_env is assigned from gov's AWS platform, does not exist in local.
    return os.environ.get("target_env")


def is_on_aws_prod():
    return get_aws_target_env() == AwsTargetEnv.PROD.value


def get_db_string():
    """retrieves a database connection string for a variety of different
    environments including:
    * local dev with postgres db
    * deployed app using amazon rds

    """

    db_conn_string = None

    if is_on_aws():
        db_conn_string = get_aws_db_string()
    else:
        db_conn_string = get_local_dev_db_string()

    # LOGGER.debug(f"Database connection url: {db_conn_string}")
    return db_conn_string


def get_aws_db_string():
    secret_value = get_aws_db_secret()
    secret_json = json.loads(secret_value["SecretString"])

    username = secret_json.get("username")
    password = secret_json.get("password")

    host = get_env_var("PG_HOST")
    port = get_env_var("PG_PORT")
    dbname = get_env_var("PG_DATABASE")
    return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}"


def get_local_dev_db_string():
    username = get_env_var("POSTGRES_USER")
    password = get_env_var("POSTGRES_PASSWORD")
    host = get_env_var("POSTGRES_HOST")
    port = get_env_var("POSTGRES_PORT")
    dbname = get_env_var("POSTGRES_DB")
    return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}"


def get_aws_region():
    env_var = "COGNITO_REGION"
    return get_env_var(env_var)


def get_bcsc_key_id():
    env_var = "BCSC_KEY_ID"
    return get_env_var(env_var)


def get_user_pool_id():
    env_var = "COGNITO_USER_POOL_ID"
    return get_env_var(env_var)


def get_user_pool_domain_name():
    env_var = "COGNITO_USER_POOL_DOMAIN"
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
            f"The required environment variable {env_var_name} has not "
            + "been populated"
        )
        super().__init__(self.message)


if __name__ == "__main__":
    var = get_user_pool_domain_name()
    print(f"var: {var}")


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
            client = session.client(
                service_name="secretsmanager", region_name=get_aws_region()
            )
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


def get_forest_client_api_token(api_env: ApiInstanceEnv = ApiInstanceEnv.TEST):
    """
    :param api_env: Api Instance caller function likes to connect to.
    """
    api_key = "FC_API_TOKEN" + "_" + api_env
    LOGGER.info(f"Using forest_client_api_token key -- {api_key}")
    api_token = get_env_var(api_key)
    return api_token


def get_forest_client_api_baseurl(api_env: ApiInstanceEnv = ApiInstanceEnv.TEST):
    """
    :param api_env: Api Instance caller function likes to connect to.
    """
    forest_client_api_baseurl = (
        get_env_var("FC_API_BASE_URL" + "_" + api_env)
        if is_on_aws()
        else "https://nr-forest-client-api-test.api.gov.bc.ca"  # test
    )

    LOGGER.info(f"Using forest_client_api_baseurl -- {forest_client_api_baseurl}")
    return forest_client_api_baseurl


def use_api_instance_by_app_env(app_env: AppEnv):
    """
    In each FAM environment (DEV/TEST/PROD), it supports applications with (DEV/TET/PROD)
    Only FAM PROD with application(PROD) use API instance in PROD.
    """
    app_instance_env = ApiInstanceEnv.TEST  # default.
    if (is_on_aws_prod() and (
        app_env == AppEnv.APP_ENV_TYPE_PROD or
        app_env == AppEnv.FAM
    )):
        app_instance_env = ApiInstanceEnv.PROD

    LOGGER.info(f"Use api instance environment -- {app_instance_env}")
    return app_instance_env


def get_idim_proxy_api_baseurl(app_env: AppEnv):
    idim_proxy_api_baseurl = get_env_var("IDIM_PROXY_BASE_URL_TEST")
    if (
        app_env == AppEnv.APP_ENV_TYPE_PROD
        and get_env_var("TARGET_ENV") == AppEnv.APP_ENV_TYPE_PROD.lower()
    ):
        # only prod application integrated with FAM PROD can verify production users
        idim_proxy_api_baseurl = get_env_var("IDIM_PROXY_BASE_URL_PROD")
    LOGGER.info(f"Using idim_proxy_api_baseurl -- {idim_proxy_api_baseurl}")
    return idim_proxy_api_baseurl


def get_idim_proxy_api_key():
    idim_proxy_api_key = get_env_var("IDIM_PROXY_API_KEY")
    return idim_proxy_api_key


def get_gc_notify_email_api_key():
    gc_notify_email_api_key = get_env_var("GC_NOTIFY_EMAIL_API_KEY")
    return gc_notify_email_api_key


# For local development, you can override this function since it doesn't work outside AWS
def is_bcsc_key_enabled():
    return os.environ.get("ENABLE_BCSC_JWKS_ENDPOINT", "True") == "True"
