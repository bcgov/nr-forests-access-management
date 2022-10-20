import os
import logging
from pickle import NONE
import jsonpickle
import boto3
import json
import psycopg2
from psycopg2 import sql

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db_connection = None
testing = False


user_type_code_dict = {
    "idir": "I",
    "bceidbusiness": "B"
}


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
        connection.autocommit = False
        db_connection = connection
    return db_connection


def release_db_connection(connection):
    if not testing:
        db_connection.commit()
        db_connection.close()

def lambda_handler(event, context):
    # logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    # logger.info('## EVENT\r' + jsonpickle.encode(event))
    # logger.info('## CONTEXT\r' + jsonpickle.encode(context))

    connection = obtain_db_connection()

    populate_user_if_necessary(connection, event, context)


    cursor = connection.cursor()
    query = """
    SELECT
        role.role_name,
        role.client_number_id,
        parent_role.role_name as parent_role
    FROM app_fam.fam_role role
         LEFT JOIN app_fam.fam_role parent_role ON role.parent_role_id = parent_role.role_id
    INNER JOIN app_fam.fam_application application ON role.application_id = application.application_id
	JOIN app_fam.fam_application_client client ON application.application_id = client.application_id
	JOIN app_fam.fam_user_role_xref role_assignment ON role.role_id = role_assignment.role_id
	JOIN app_fam.fam_user user_assigned ON role_assignment.user_id = user_assigned.user_id
	WHERE user_assigned.user_guid = {user_guid}
	AND user_assigned.user_type_code = {user_type_code}
	AND client.cognito_client_id = {cognito_client_id};
    """
    user_guid = event['request']['userAttributes']['custom:idp_user_id']
    user_type_code = user_type_code_dict[event['request']['userAttributes']['custom:idp_name']]
    cognito_client_id = event['callerContext']['clientId']


    sql_query = sql.SQL(query).format(
        user_guid = sql.Literal(user_guid),
        user_type_code = sql.Literal(user_type_code),
        cognito_client_id = sql.Literal(cognito_client_id))

    cursor.execute(sql_query)
    roleList = []
    for record in cursor:
        roleList.append(record[0])

    # query_result = cursor.fetchone()
    # app_description = query_result[0]

    release_db_connection(connection)

    event["response"]["claimsOverrideDetails"] = {
        "groupOverrideDetails": {
            "groupsToOverride": roleList,
            "iamRolesToOverride": [],
            "preferredRole": ""
            }
        }
    return event

def populate_user_if_necessary(connection, event, context):
    user_type = event['request']['userAttributes']['custom:idp_name']
    user_guid = event['request']['userAttributes']['custom:idp_user_id']
    cognito_user_id = event['userName']
    user_name = event['request']['userAttributes']['custom:idp_username']

    user_type_code_dict = {
        "idir": "I",
        "bceidbusiness": "B"
    }
    user_type_code = user_type_code_dict[user_type]

    raw_query = '''INSERT INTO app_fam.fam_user
        (user_type_code, user_guid, cognito_user_id, user_name,
        create_user, create_date, update_user, update_date)
        VALUES( {user_type_code}, {user_guid}, {cognito_user_id}, {user_name},
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE)
        ON CONFLICT ON CONSTRAINT fam_usr_uk DO
        UPDATE SET user_guid = {user_guid},  cognito_user_id = {cognito_user_id};'''

    sql_query = sql.SQL(raw_query).format(
        user_type_code = sql.Literal(user_type_code),
        user_guid = sql.Literal(user_guid),
        cognito_user_id = sql.Literal(cognito_user_id),
        user_name = sql.Literal(user_name))

    connection.cursor().execute(sql_query)
