import logging
import os
import sys

from constant import TEST_ROLE_NAME

modulePath = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(modulePath)
import lambda_function


LOGGER = logging.getLogger(__name__)


def format_user_properties(cognito_event):
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
    return test_user_properties


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


def initial_user(db_pg_transaction, cognito_event):
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


def create_user_role_xref_record(db_pg_transaction, test_user_properties):
    cursor = db_pg_transaction.cursor()
    raw_query = """
    insert into app_fam.fam_user_role_xref
        (user_id,
        role_id,
        create_user,
        update_user)
    VALUES (
        (select user_id from app_fam.fam_user where
            user_name = %s
            and user_type_code = %s),
        (select role_id from app_fam.fam_role where
            role_name = %s),
        CURRENT_USER,
        CURRENT_USER
    )
    """
    # For Insert statement, pass parameters as .execute()'s second arguments so they get proper sanitization.
    cursor.execute(
        raw_query,
        (
            test_user_properties.get("idp_username"),
            test_user_properties.get("idp_type_code"),
            TEST_ROLE_NAME,
        ),
    )
