import os
import logging
import boto3
import base64
from botocore.exceptions import ClientError

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
        return SQLALCHEMY_DATABASE_URL

    # if the POSTGRESQL_USER env var is populated then use a postgres
    if "POSTGRES_USER" in os.environ:
        SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}" + \
            f":{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/" + \
            f"{POSTGRES_DB}"
        LOGGER.debug(f"db conn str: {SQLALCHEMY_DATABASE_URL}")
        return SQLALCHEMY_DATABASE_URL

    if "DB_SECRET" in os.environ:
        SECRET_VALUE = get_secret()

        # TODO parse this as json. secret_value.username, secret_value.password

        # TODO Really bad because this logs password.
        LOGGER.debug(f"secret_value: {SECRET_VALUE}")

        # TODO: set up environment entry in fam_ap.tf to populate this from db_name variable in variables.tf
        DB_NAME=os.environ["DB_NAME"]

        # TODO: fix this to use information from secret. Also don't currently have hostname in secret.
        RDS_HOST="fam-aurora-db-postgres.cluster-cp9oqzf51oiq.ca-central-1.rds.amazonaws.com"
        RDS_PORT="5432"
        AWS_RDS_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}" + \
            f":{POSTGRES_PASSWORD}@{RDS_HOST}:{RDS_PORT}/" + \
            f"{DB_NAME}"
        LOGGER.debug(f"db conn str: {AWS_RDS_DATABASE_URL}")
        return AWS_RDS_DATABASE_URL

def get_secret():
    # Use this code snippet in your app.
    # If you need more information about configurations or implementing the sample code, visit the AWS docs:   
    # https://aws.amazon.com/developers/getting-started/python/

    secret_name = os.environ["DB_SECRET"]
    region_name = "ca-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret;
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret;

    raise "Should never reach";
