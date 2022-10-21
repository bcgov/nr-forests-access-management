import json
import logging
import os

import lambda_function
import psycopg2
import pytest

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def db_connection():
    LOGGER.debug("test log message")
    user4tests = "fam_proxy_api"
    user4tests = "postgres"  # override for kevins config

    dbName = "postgres"
    dbName = "fam"  # override for kevins config
    connection = psycopg2.connect(
        host=os.environ.get("PG_HOST", "localhost"),
        port=os.environ.get("PG_PORT", "5432"),
        dbname=os.environ.get("PG_DATABASE", dbName),
        user=os.environ.get("PG_USER", user4tests),
        password=os.environ.get("PG_PASSWORD", "postgres"),
        sslmode="disable",
    )
    # dbname='fam')
    connection.autocommit = False  # With tests we don't need to clean up the data
    lambda_function.db_connection = connection
    lambda_function.testing = True
    yield connection
    # Do a monkeypatch on get get db and finalize db methods
    connection.close()


@pytest.fixture(scope="function")
def db_transaction(db_connection):
    yield db_connection
    db_connection.rollback()


@pytest.fixture(scope="session")
def context():
    context = {"requestid": "1234"}
    yield context


@pytest.fixture(scope="function")
def event():
    event_file_path = os.path.join(os.path.dirname(__file__), "login_event.json")
    # event_file_path = "./login_event.json"

    file = open(event_file_path, "r")
    try:
        # event = jsonpickle.decode(file.read())
        event = json.load(file)
    finally:
        file.close()
    yield event


@pytest.fixture(scope="function")
def test_user_properties(event):
    userAtribs = event["request"]["userAttributes"]
    test_user_properties = {}
    test_user_properties["idp_user_id"] = userAtribs["custom:idp_name"]
    test_user_properties["idp_type_code"] = lambda_function.user_type_code_dict[
        test_user_properties["idp_user_id"]
    ]
    test_user_properties["idp_user_id"] = userAtribs["custom:idp_user_id"]
    test_user_properties["idp_username"] = userAtribs["custom:idp_username"]
    test_user_properties["cognito_user_id"] = event["userName"]
    return test_user_properties


@pytest.fixture(scope="function")
def initial_user_without_guid_or_cognito_id(
    db_transaction, event, test_user_properties
):
    # global test_user_properties
    initial_user = test_user_properties

    # Only insert the bare minimum to simulate entering user in advance of first login

    raw_query = """INSERT INTO app_fam.fam_user
        (user_type_code, user_name,
        create_user, create_date, update_user, update_date)
        VALUES( '{}', '{}',
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE);"""
    # print(f"query is\n:{raw_query}")

    idpName = event["request"]["userAttributes"]["custom:idp_name"]
    replaced_query = raw_query.format(
        lambda_function.user_type_code_dict[idpName],
        event["request"]["userAttributes"]["custom:idp_username"],
    )
    db_transaction.cursor().execute(replaced_query)

    yield initial_user


@pytest.fixture(scope="function")
def initial_user(db_connection, db_transaction, event, test_user_properties):
    # global test_user_properties
    initial_user = test_user_properties

    # Only insert the bare minimum to simulate entering user in advance of first login

    raw_query = """INSERT INTO app_fam.fam_user
        (user_type_code, user_name, user_guid,
        create_user, create_date, update_user, update_date)
        VALUES( '{}', '{}', '{}',
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE);"""
    # print(f"query is\n:{raw_query}")

    idpName = event["request"]["userAttributes"]["custom:idp_name"]
    replaced_query = raw_query.format(
        lambda_function.user_type_code_dict[idpName],
        event["request"]["userAttributes"]["custom:idp_username"],
        event["request"]["userAttributes"]["custom:idp_user_id"],
    )

    # initial_user["idp_type_code"],
    # initial_user["idp_username"])
    db_connection.cursor().execute(replaced_query)

    yield initial_user


@pytest.fixture(scope="function")
def test_role_name():
    expected_role = "EXPECTED"
    return expected_role


@pytest.fixture(scope="function")
def create_test_fam_role(db_transaction, test_role_name):
    """does the database setup to insert a new test role into the database
    table fam_role.

    :param db_transaction: _description_
    :type db_transaction: _type_
    :param test_role_name: _description_
    :type test_role_name: _type_
    """

    expected_role = test_role_name
    # Set up expected role in DB
    cursor = db_transaction.cursor()
    raw_query = """
    insert into app_fam.fam_role
        (role_name,
         role_purpose,
         application_id,
         role_type_code,
         create_user,
         update_user)
    values
        ('{}',
        'just for testing',
        (select application_id from app_fam.fam_application
            where application_name = 'fam'),
        'C',
        CURRENT_USER,
        CURRENT_USER)
    """
    replaced_query = raw_query.format(expected_role)
    cursor.execute(replaced_query)


@pytest.fixture(scope="function")
def create_test_fam_cognito_client(db_transaction, event):
    """database set up to create fam test cognito client"""
    clientId = event["callerContext"]["clientId"]
    cursor = db_transaction.cursor()
    # Set up expected client in DB
    # cursor = db_transaction.cursor()
    raw_query = """
    insert into app_fam.fam_application_client
        (cognito_client_id,
        application_id,
        create_user,
        update_user)
    values(
        '{}',
        (select application_id from app_fam.fam_application
            where application_name = 'fam'),
        CURRENT_USER,
        CURRENT_USER)
    """
    replaced_query = raw_query.format(clientId)
    cursor.execute(replaced_query)


@pytest.fixture(scope="function")
def create_user_role_xref_record(db_transaction, test_user_properties, test_role_name):
    initial_user = test_user_properties
    cursor = db_transaction.cursor()
    raw_query = """
    insert into app_fam.fam_user_role_xref
        (user_id,
        role_id,
        create_user,
        update_user)
    VALUES (
        (select user_id from app_fam.fam_user where
            user_name = '{}'
            and user_type_code = '{}'),
        (select role_id from app_fam.fam_role where
            role_name = '{}'),
        CURRENT_USER,
        CURRENT_USER
    )
    """
    replaced_query = raw_query.format(
        initial_user["idp_username"], initial_user["idp_type_code"], test_role_name
    )
    cursor.execute(replaced_query)
