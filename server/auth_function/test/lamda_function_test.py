import pytest
import psycopg2
import os
import sys
import logging
import jsonpickle
import pathlib
from psycopg2 import sql
import fixtures

logger = logging.getLogger()
logger.setLevel(logging.INFO)

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent))
function = __import__('lambda_function')
handler = function.lambda_handler

@pytest.fixture(scope='session')
def db_connection():
    connection = psycopg2.connect(host=os.environ.get('PG_HOST', 'localhost'),
                                  port=os.environ.get('PG_PORT', '5432'),
                                  dbname=os.environ.get('PG_DATABASE', 'postgres'),
                                  user=os.environ.get('PG_USER', 'fam_proxy_api'),
                                  password=os.environ.get('PG_PASSWORD', 'test'),
                                  sslmode='disable')
    connection.autocommit = False  # With tests we don't need to clean up the data
    function.db_connection = connection
    function.testing = True
    yield connection
    # Do a monkeypatch on get get db and finalize db methods
    connection.close()

@pytest.fixture(scope='function')
def db_transaction(db_connection):
    yield db_connection
    db_connection.rollback()

@pytest.fixture(scope='session')
def context():
    context = {'requestid' : '1234'}
    yield context

@pytest.fixture(scope='function')
def event():
    event_file_path = str(current_dir) + "/login_event.json"
    file = open(event_file_path)
    try:
        event = jsonpickle.decode(file.read())
    finally:
        file.close()
    yield event

test_user_properties = {
    "idp_type_code": "I",
    "idp_name": "idir",
    "idp_user_id": "B5ECDB094DFB4149A6A8445A01A96BF0",
    "idp_username": "COGUSTAF",
    "cognito_user_id": "idir_b5ecdb094dfb4149a6a8445a01a96bf0@idir", 
}

@pytest.fixture(scope='function')
def initial_user(db_connection, db_transaction):
    global test_user_properties
    initial_user = test_user_properties

    # Only insert the bare minimum to simulate entering user in advance of first login

    raw_query = '''INSERT INTO app_fam.fam_user
        (user_type_code, user_name, 
        create_user, create_date, update_user, update_date)
        VALUES( '{}', '{}', 
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE);'''

    replaced_query = raw_query.format(
        initial_user["idp_type_code"], 
        initial_user["idp_username"])
    db_connection.cursor().execute(replaced_query)

    yield initial_user

def test_create_user_if_not_found(db_connection, db_transaction, context, event):

    global test_user_properties

    test_idp_type_code = test_user_properties["idp_type_code"]
    test_idp_user_id = test_user_properties["idp_user_id"] 
    test_cognito_user_id = test_user_properties["cognito_user_id"]
    test_idp_username = test_user_properties["idp_username"] 

    # setup

    # execute
    result = handler(event, context)

    # validate that there is one user in the database with the properties from the incoming event
    cursor = db_connection.cursor()
    raw_query = '''select count(*) from app_fam.fam_user where 
        user_type_code = {} and 
        user_guid = {} and 
        cognito_user_id = {} and
        user_name = {};'''
    replaced_query = sql.SQL(raw_query).format(
        sql.Literal(test_idp_type_code), 
        sql.Literal(test_idp_user_id), 
        sql.Literal(test_cognito_user_id), 
        sql.Literal(test_idp_username))
    cursor.execute(replaced_query)

    count = cursor.fetchone()[0]

    assert count == 1


def test_update_user_if_already_exists(db_connection, db_transaction, context, event, initial_user):

    global test_user_properties

    test_idp_type_code = test_user_properties["idp_type_code"]
    test_idp_user_id = test_user_properties["idp_user_id"] 
    test_cognito_user_id = test_user_properties["cognito_user_id"]
    test_idp_username = test_user_properties["idp_username"] 

    # setup

    # execute
    result = handler(event, context)

    # validate that there is one user in the database with the properties from the incoming event
    cursor = db_connection.cursor()
    raw_query = '''select count(*) from app_fam.fam_user where 
        user_type_code = {} and 
        user_guid = {} and 
        cognito_user_id = {} and
        user_name = {};'''
    query = sql.SQL(raw_query).format(
        sql.Literal(test_idp_type_code), 
        sql.Literal(test_idp_user_id), 
        sql.Literal(test_cognito_user_id), 
        sql.Literal(test_idp_username))
    cursor.execute(query)

    count = cursor.fetchone()[0]

    assert count == 1

def test_single_parent_role_found(db_connection, db_transaction, context, event, initial_user):

    # setup
    expected_role = 'EXPECTED'

    # Set up expected role in DB
    cursor = db_connection.cursor()
    raw_query = '''insert into app_fam.fam_role 
        (role_name, role_purpose, application_id, role_type_code, create_user, update_user)
        values( '{}', 'just for testing', (select application_id from app_fam.fam_application where application_name = 'fam'), 'C', CURRENT_USER, CURRENT_USER);'''
    replaced_query = raw_query.format(expected_role)
    db_connection.cursor().execute(replaced_query)

    # Set up expected client in DB
    cursor = db_connection.cursor()
    raw_query = '''insert into app_fam.fam_application_client 
        (cognito_client_id, application_id, create_user, update_user)
        values( '{}', (select application_id from app_fam.fam_application where application_name = 'fam'), CURRENT_USER, CURRENT_USER);'''
    replaced_query = raw_query.format('3u3vm7ehhaj2iqkm851t8fl6gp')
    db_connection.cursor().execute(replaced_query)

    # execute
    result = handler(event, context)

    # validate that there is one user in the database with the properties from the incoming event
    override_groups = result['response']['claimsOverrideDetails']['groupOverrideDetails']['groupsToOverride']
    assert expected_role in override_groups


