import os
import logging
import boto3
import json

LOGGER = logging.getLogger(__name__)


def getDBString():

    secret_value = get_secret()
    secret_json = json.loads(secret_value['SecretString'])
    username = secret_json['username']
    password = secret_json['password']

    host=os.environ.get('PG_HOST')
    port=os.environ.get('PG_PORT')
    dbname=os.environ.get('PG_DATABASE')

    SQLALCHEMY_DATABASE_URL = os.getenv("DB_CONN")
    if not SQLALCHEMY_DATABASE_URL:
        SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{username}" + \
        f":{password}@{host}:{port}/" + \
        f"{dbname}"
        
    #     # force default sqllite database if not POSTGRES vars not defined
    #     curdir = os.path.dirname(__file__)
    #     databaseFile = os.path.join(curdir, "..", "fam.db")
    #     LOGGER.debug(f"databaseFile: {databaseFile}")
    #     SQLALCHEMY_DATABASE_URL = f"sqlite:///{databaseFile}"
    #     LOGGER.debug(f"SQLALCHEMY_DATABASE_URL: {SQLALCHEMY_DATABASE_URL}")

    # # if the POSTGRESQL_USER env var is populated then use a postgres
    # if "POSTGRES_USER" in os.environ:
    #     SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}" + \
    #         f":{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/" + \
    #         f"{POSTGRES_DB}"
    #     LOGGER.debug(f"db conn str: {SQLALCHEMY_DATABASE_URL}")

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

    return client.get_secret_value( SecretId=secret_name )
