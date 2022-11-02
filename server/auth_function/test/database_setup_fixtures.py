import json
import logging
import os

import config
import lambda_function
import pytest

LOGGER = logging.getLogger(__name__)

# issues with mixing session and function
@pytest.fixture(scope="function")
def auth_object(cognito_event):
    auth_obj = lambda_function.AuthorizationQuery(event=cognito_event,
                                                  testing=True)
    yield auth_obj
    # rollback connections
    auth_obj.db_connection.rollback()


# @pytest.fixture(scope="session")
# def database_connection_string():
#     db_conn_string = config.get_db_connection_string()
#     return db_conn_string


# @pytest.fixture(scope="session")
# def db_connection(database_connection_string):
#     LOGGER.debug("test log message")
#      lambda_function.testing = True
#     connection = lambda_function.obtain_db_connection()
#     yield connection
#     # Do a monkeypatch on get get db and finalize db methods
#     connection.close()


# @pytest.fixture(scope="function")
# def db_transaction(db_connection):
#     yield db_connection
#     db_connection.rollback()


@pytest.fixture(scope="session")
def context():
    context = {"requestid": "1234"}
    yield context


@pytest.fixture(scope="function")
def cognito_event():
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
def test_user_properties(auth_object):
    cognito_event = auth_object.event
    userAtribs = cognito_event["request"]["userAttributes"]
    test_user_properties = {}
    test_user_properties["idp_type_code"] = auth_object.user_type_code_dict[
        userAtribs["custom:idp_name"]
    ]
    test_user_properties["idp_user_id"] = userAtribs["custom:idp_user_id"]
    test_user_properties["idp_username"] = userAtribs["custom:idp_username"]

    test_user_properties["cognito_user_id"] = cognito_event["userName"]
    return test_user_properties


@pytest.fixture(scope="function")
def initial_user_without_guid_or_cognito_id(
    auth_object, test_user_properties
):
    initial_user = test_user_properties
    db = auth_object.db_connection
    event = auth_object.event

    # Only insert the bare minimum to simulate entering user in advance of first login

    raw_query = """INSERT INTO app_fam.fam_user
        (user_type_code, user_name,
        create_user, create_date, update_user, update_date)
        VALUES( '{}', '{}',
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE);"""
    # print(f"query is\n:{raw_query}")

    idpName = event["request"]["userAttributes"]["custom:idp_name"]
    replaced_query = raw_query.format(
        auth_object.user_type_code_dict[idpName],
        event["request"]["userAttributes"]["custom:idp_username"],
    )
    db.cursor().execute(replaced_query)

    yield initial_user


@pytest.fixture(scope="function")
def initial_user(auth_object, test_user_properties):
    # global test_user_properties
    initial_user = test_user_properties
    event = auth_object.event
    db = auth_object.db_connection

    # Only insert the bare minimum to simulate entering user in advance of first login

    raw_query = """INSERT INTO app_fam.fam_user
        (user_type_code, user_name, user_guid,
        create_user, create_date, update_user, update_date)
        VALUES( '{}', '{}', '{}',
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE);"""
    # print(f"query is\n:{raw_query}")

    idpName = event["request"]["userAttributes"]["custom:idp_name"]
    replaced_query = raw_query.format(
        auth_object.user_type_code_dict[idpName],
        event["request"]["userAttributes"]["custom:idp_username"],
        event["request"]["userAttributes"]["custom:idp_user_id"],
    )

    # initial_user["idp_type_code"],
    # initial_user["idp_username"])
    db.cursor().execute(replaced_query)

    yield initial_user


@pytest.fixture(scope="function")
def test_role_name():
    expected_role = "EXPECTED"
    return expected_role


@pytest.fixture(scope="function")
def create_test_fam_role(auth_object, test_role_name):
    """does the database setup to insert a new test role into the database
    table fam_role.

    :param db_transaction: _description_
    :type db_transaction: _type_
    :param test_role_name: _description_
    :type test_role_name: _type_
    """

    expected_role = test_role_name
    db = auth_object.db_connection

    # Set up expected role in DB
    cursor = db.cursor()
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
    get_insert_role_sql(expected_role, 'C')
    replaced_query = raw_query.format(expected_role)
    cursor.execute(replaced_query)

@pytest.fixture(scope="function")
def create_fam_child_parent_role_assignment(auth_object):
    """
    * creates a parent role (type = A, abstract),
    * retrieve the role_id for the role just created
    * create child role with the (type=C concrete) with parent_id = initally
      created role

    :param auth_object: _description_
    :type auth_object: _type_
    :return: _description_
    :rtype: _type_
    """
    cur = auth_object.db_connection.cursor()

    parent_role_name = 'test_parent_role'
    child_role_name = 'test_child_role'
    insert_parent_role_sql = get_insert_role_sql(role_name=parent_role_name,
                                                 role_type='A')
    cur.execute(insert_parent_role_sql)

    query = "select role_id from app_fam.fam_role " + \
            f"where role_name = '{parent_role_name}'"
    cur.execute(query)
    parent_role_id = cur.fetchone()[0]
    LOGGER.debug(f"record: {parent_role_id}")

    insert_parent_role_sql = get_insert_role_sql(role_name=child_role_name,
                                                 role_type='C',
                                                 parent_role_id=parent_role_id)
    cur.execute(insert_parent_role_sql)

    yield auth_object

@pytest.fixture(scope="function")
def create_test_forest_client_role(auth_object):
    yield 'junk'


@pytest.fixture(scope="function")
def create_test_fam_cognito_client(auth_object):
    """database set up to create fam test cognito client"""
    event = auth_object.event
    db = auth_object.db_connection

    clientId = event["callerContext"]["clientId"]
    cursor = db.cursor()
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
def create_user_role_xref_record(auth_object, test_user_properties, test_role_name):
    initial_user = test_user_properties
    db = auth_object.db_connection
    cursor = db.cursor()
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


def get_insert_role_sql(role_name, role_type, parent_role_id=None):
    parent_column = ''
    parent_value = ''
    if parent_role_id:
        parent_column = ',parent_role_id'
        parent_value = ',' + str(parent_role_id)
    raw_query = f"""
    insert into app_fam.fam_role
        (role_name,
         role_purpose,
         application_id,
         role_type_code,
         create_user,
         update_user {parent_column})
    values
        ('{role_name}',
        'just for testing',
        (select application_id from app_fam.fam_application
            where application_name = 'fam'),
        '{role_type}',
        CURRENT_USER,
        CURRENT_USER {parent_value})
    """
    return raw_query

def get_role_sql(role_name):
    pass


