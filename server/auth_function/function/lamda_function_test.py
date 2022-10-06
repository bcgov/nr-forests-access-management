import pytest
import psycopg2
import os
import logging
import jsonpickle

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

# @pytest.fixture(scope='function')
# def fam_user(db_connection, db_transaction):

#     #insert a fam user

    

def test_find_app_description(db_connection, db_transaction):

    # setup
    file = open('login_event.json')
    try:
        event = jsonpickle.decode(file.read())
        context = {'requestid' : '1234'}
    finally:
        file.close()

    # execute
    result = handler(event, context)

    # assert
    actual_app_description = event['response']['claimsOverrideDetails']['claimsToAddOrOverride']['famAuthorization']['appDescription']

    cursor = db_connection.cursor()
    cursor.execute("select application_description description from app_fam.fam_application app where app.application_name = 'fam';")
    appQueryResult = cursor.fetchone()
    expected_app_description = appQueryResult[0]

    assert expected_app_description == actual_app_description

    



