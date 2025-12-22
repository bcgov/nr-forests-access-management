import json
import logging
import os
import sys

import dotenv
import psycopg2
import pytest
from constant import TEST_ROLE_NAME
from psycopg2 import sql
from testcontainers.compose import DockerCompose

modulePath = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(modulePath)
import lambda_function  # noqa - need import here to make avail to fixtures/tests

LOGGER = logging.getLogger(__name__)
COMPOSE_PATH = os.path.join(os.path.dirname(__file__), "../../../")
COMPOSE_FILE_NAME = "docker-compose-testcontainer.yml"


# Start a docker compose session to have an in-container DB with flyway applied
@pytest.fixture(scope="session")
def db_pg_container():
    compose = DockerCompose(COMPOSE_PATH, compose_file_name=COMPOSE_FILE_NAME)
    compose.start()
    # NGINX is set to start only when flyway is complete
    compose.wait_for("http://localhost:8181")
    yield compose
    compose.stop()


def get_local_db_string():
    # read the env file if it exists
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        dotenv.load_dotenv(env_file)

    # if the env vars are populated they will take precidence, otherwise
    # the values identified here will be used
    # need to use postgres user to run the tests, fam_proxy_api does not have the privilege anymore
    username = os.getenv("POSTGRES_USER", "postgres")  # fam_proxy_api
    password = os.getenv("POSTGRES_PASSWORD", "postgres")  # test
    host = os.getenv("POSTGRES_HOST", "localhost")
    dbname = os.getenv("POSTGRES_DB", "fam")
    port = os.getenv("POSTGRES_PORT_TESTCONTAINER", "5433")

    db_conn_string = (
        f"user={username} password={password} host={host} "
        + f"port={port} dbname ={dbname}"
    )

    return db_conn_string


# Create one database session for all the tests to use
@pytest.fixture(scope="session")
def db_pg_connection(db_pg_container):
    db_connection_string = get_local_db_string()
    db_connection = psycopg2.connect(db_connection_string, sslmode="disable")
    db_connection.autocommit = False
    yield db_connection
    db_connection.close()


# Use this fixture in tests so that each test does a rollback at the end
@pytest.fixture(scope="function")
def db_pg_transaction(db_pg_connection, monkeypatch):
    # Override the methods that the auth function uses to handle transactions
    monkeypatch.setattr(
        lambda_function, "obtain_db_connection", lambda: db_pg_connection
    )
    monkeypatch.setattr(lambda_function, "release_db_connection", lambda db: None)

    yield db_pg_connection
    db_pg_connection.rollback()


# Load a sample cognito test event if necessary
@pytest.fixture(scope="session")
def cognito_event(request):
    event_file_path = os.path.join(os.path.dirname(__file__), request.param)

    with open(event_file_path, "r") as file:
        event = json.load(file)

    yield event


# Load a sample cognito fixture if necessary
@pytest.fixture(scope="session")
def cognito_context():
    context = {"requestid": "1234"}
    yield context


@pytest.fixture(scope="session")
def test_user_properties(cognito_event):
    user_attribs = cognito_event["request"]["userAttributes"]
    test_user_properties = {}
    test_user_properties["idp_type_code"] = lambda_function.USER_TYPE_CODE_DICT[
        user_attribs.get("custom:idp_name")
    ]
    test_user_properties["idp_user_id"] = user_attribs.get("custom:idp_user_id")
    # set "idp_username" to be "custom:idp_user_id" when "custom:idp_username" not exists for bcsc user
    # in lambda_function, when we create user for bcsc login, we also use "custom:idp_user_id" for the "idp_username"
    test_user_properties["idp_username"] = (
        user_attribs.get("custom:idp_username")
        if user_attribs.get("custom:idp_username")
        else user_attribs.get("custom:idp_user_id")
    )

    test_user_properties["cognito_user_id"] = cognito_event["userName"]
    test_user_properties["idp_business_id"] = user_attribs.get("custom:idp_business_id")
    test_user_properties["email"] = user_attribs.get("email")
    return test_user_properties


@pytest.fixture(scope="function")
def initial_user(db_pg_transaction, cognito_event, test_user_properties):
    cursor = db_pg_transaction.cursor()

    raw_query = """INSERT INTO app_fam.fam_user
        (user_type_code, user_name, user_guid,
        create_user, create_date, update_user, update_date)
        VALUES( %s, %s, %s,
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE);"""
    # print(f"query is\n:{raw_query}")

    idp_name = cognito_event["request"]["userAttributes"].get("custom:idp_name")
    # set "username" to be "custom:idp_user_id" when "custom:idp_username" not exists for bcsc user
    user_name = (
        cognito_event["request"]["userAttributes"].get("custom:idp_username")
        if cognito_event["request"]["userAttributes"].get("custom:idp_username")
        else cognito_event["request"]["userAttributes"].get("custom:idp_user_id")
    )
    # For Insert statement, pass parameters as .execute()'s second arguments so they get proper sanitization.
    cursor.execute(
        raw_query,
        (
            lambda_function.USER_TYPE_CODE_DICT[idp_name],
            user_name,
            cognito_event["request"]["userAttributes"].get("custom:idp_user_id"),
        ),
    )

    yield test_user_properties


@pytest.fixture(scope="function")
def create_test_fam_role(db_pg_transaction):
    def _create_test_fam_role(role_name=TEST_ROLE_NAME):
        cursor = db_pg_transaction.cursor()
        raw_query = """
        insert into app_fam.fam_role
            (role_name,
             role_purpose,
             application_id,
             role_type_code,
             create_user,
             update_user)
        values
            (%s,
            'just for testing',
            (select application_id from app_fam.fam_application
                where application_name = 'FAM'),
            'C',
            CURRENT_USER,
            CURRENT_USER)
        """
        cursor.execute(raw_query, [role_name])
    return _create_test_fam_role


def get_insert_role_sql(role_name, role_type, parent_role_id=None):
    parent_column = ""
    parent_value = ""
    if parent_role_id:
        parent_column = ",parent_role_id"
        parent_value = "," + str(parent_role_id)
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
            where application_name = 'FAM'),
        '{role_type}',
        CURRENT_USER,
        CURRENT_USER {parent_value})
    """
    return raw_query


@pytest.fixture(scope="function")
def create_test_fam_cognito_client(db_pg_transaction, cognito_event):
    client_id = cognito_event["callerContext"]["clientId"]
    cursor = db_pg_transaction.cursor()
    # Set up expected client in DB
    # cursor = db_transaction.cursor()
    raw_query = """
    insert into app_fam.fam_application_client
        (cognito_client_id,
        application_id,
        create_user,
        update_user)
    values(
        %s,
        (select application_id from app_fam.fam_application
            where application_name = 'FAM'),
        CURRENT_USER,
        CURRENT_USER)
    """
    # For Insert statement, pass parameters as .execute()'s second arguments so they get proper sanitization.
    cursor.execute(raw_query, [client_id])


@pytest.fixture(scope="function")
def create_user_role_xref_record(db_pg_transaction, test_user_properties):
    def _create_user_role_xref_record(role_name=TEST_ROLE_NAME, expiry_date=None):
        initial_user = test_user_properties
        cursor = db_pg_transaction.cursor()
        raw_query = """
        insert into app_fam.fam_user_role_xref
            (user_id,
            role_id,
            expiry_date,
            create_user,
            update_user)
        VALUES (
            (select user_id from app_fam.fam_user where
                user_name = %s
                and user_type_code = %s),
            (select role_id from app_fam.fam_role where
                role_name = %s),
            %s,
            CURRENT_USER,
            CURRENT_USER
        )
        """
        cursor.execute(
            raw_query,
            (
                initial_user.get("idp_username"),
                initial_user.get("idp_type_code"),
                role_name,
                expiry_date,
            ),
        )
    return _create_user_role_xref_record

@pytest.fixture(scope="function")
def create_fam_application_admin_record(db_pg_transaction, test_user_properties):
    initial_user = test_user_properties
    cursor = db_pg_transaction.cursor()
    raw_query = """
    insert into app_fam.fam_application_admin
        (user_id,
        application_id,
        create_user,
        update_user)
    VALUES (
        (select user_id from app_fam.fam_user where
            user_name = %s
            and user_type_code = %s),
        (select application_id from app_fam.fam_application
            where application_name = 'FAM'),
        CURRENT_USER,
        CURRENT_USER
    )
    """
    cursor.execute(
        raw_query,
        (
            initial_user.get("idp_username"),
            initial_user.get("idp_type_code")
        ),
    )


@pytest.fixture(scope="function")
def initial_user_without_guid_or_cognito_id(db_pg_transaction, cognito_event):
    cursor = db_pg_transaction.cursor()

    # Only insert the bare minimum to simulate entering user in advance of first login

    raw_query = """INSERT INTO app_fam.fam_user
        (user_type_code, user_name,
        create_user, create_date, update_user, update_date)
        VALUES( %s, %s,
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE);"""
    # print(f"query is\n:{raw_query}")

    idp_name = cognito_event["request"]["userAttributes"].get("custom:idp_name")
    # set "username" to be "custom:idp_user_id" when "custom:idp_username" not exists for bcsc user
    user_name = (
        cognito_event["request"]["userAttributes"].get("custom:idp_username")
        if cognito_event["request"]["userAttributes"].get("custom:idp_username")
        else cognito_event["request"]["userAttributes"].get("custom:idp_user_id")
    )

    cursor.execute(
        raw_query, (lambda_function.USER_TYPE_CODE_DICT[idp_name], user_name)
    )


@pytest.fixture(scope="function")
def create_fam_child_parent_role_assignment(db_pg_transaction):
    """
    * creates a parent role (type = A, abstract),
    * retrieve the role_id for the role just created
    * create child role with the (type=C concrete) with parent_id = initally
      created role
    """

    cur = db_pg_transaction.cursor()

    parent_role_name = "test_parent_role"
    child_role_name = TEST_ROLE_NAME
    insert_parent_role_sql = get_insert_role_sql(
        role_name=parent_role_name, role_type="A"
    )
    cur.execute(insert_parent_role_sql)

    query = sql.SQL(
        """select role_id from app_fam.fam_role where
           role_name = {0}"""
    ).format(sql.Literal(parent_role_name))

    cur.execute(query)
    parent_role_id = cur.fetchone()[0]
    LOGGER.debug(f"record: {parent_role_id}")

    insert_parent_role_sql = get_insert_role_sql(
        role_name=child_role_name, role_type="C", parent_role_id=parent_role_id
    )
    cur.execute(insert_parent_role_sql)
