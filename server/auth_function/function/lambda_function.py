import os
import logging
from pickle import NONE
import jsonpickle
import boto3
import json
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db_connection = None
testing = False

def obtain_db_connection():
    global db_connection

    if db_connection is None:
        secret_name = os.environ.get('DB_SECRET')
        region_name = "ca-central-1"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        secret_value = client.get_secret_value( SecretId=secret_name )
        secret_json = json.loads(secret_value['SecretString'])
        username = secret_json['username']
        password = secret_json['password']

        connection = psycopg2.connect(host=os.environ.get('PG_HOST'),
                                        port=os.environ.get('PG_PORT'),
                                        dbname=os.environ.get('PG_DATABASE'),
                                        user=username,
                                        password=password,
                                        sslmode='disable')
        connection.autocommit = False  # Ensure data is added to the database immediately after write commands
        
        db_connection = connection
    return db_connection


def release_db_connection(connection):
    if not testing:
        db_connection.commit()
        db_connection.close()

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))

    # grab requestor's email address
    # email = event['request']['userAttributes']['email']

    connection = obtain_db_connection()
    cursor = connection.cursor()
    cursor.execute("select application_description description from app_fam.fam_application app where app.application_name = 'fam';")
    query_result = cursor.fetchone()
    app_description = query_result[0]

    release_db_connection(connection)
    
    event["response"]["claimsOverrideDetails"] = { 
        "claimsToAddOrOverride": { 
            "famAuthorization": {
                "appDescription": app_description 
            }
        } 
    }
         
    return event
