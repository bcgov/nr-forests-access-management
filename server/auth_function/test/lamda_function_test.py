import os
import sys
import logging
import pprint
from psycopg2 import sql

modulePath = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(modulePath)
import lambda_function # noqa


LOGGER = logging.getLogger(__name__)


def test_create_user_if_not_found(
    db_connection, db_transaction, context, event, test_user_properties
):
    """
    test to make sure that if the user doesn't exist in the database it will
    be created.

    :param db_connection: _description_
    :type db_connection: _type_
    :param db_transaction: _description_
    :type db_transaction: _type_
    :param context: _description_
    :type context: _type_
    :param event: _description_
    :type event: _type_
    :param test_user_properties: _description_
    :type test_user_properties: _type_
    """

    test_idp_type_code = test_user_properties["idp_type_code"]
    test_idp_user_id = test_user_properties["idp_user_id"]
    test_cognito_user_id = test_user_properties["cognito_user_id"]
    test_idp_username = test_user_properties["idp_username"]

    # setup

    # execute
    lambda_function.lambda_handler(event, context)

    # validate that there is one user in the database with the properties from
    # the incoming event
    cursor = db_connection.cursor()
    raw_query = """select count(*) from app_fam.fam_user where
    # potentially another way to handle params:
    #   https://www.psycopg.org/psycopg3/docs/basic/params.html
        user_type_code = {} and
        user_guid = {} and
        cognito_user_id = {} and
        user_name = {};"""
    replaced_query = sql.SQL(raw_query).format(
        sql.Literal(test_idp_type_code),
        sql.Literal(test_idp_user_id),
        sql.Literal(test_cognito_user_id),
        sql.Literal(test_idp_username),
    )
    cursor.execute(replaced_query)

    count = cursor.fetchone()[0]

    assert count == 1


def test_update_user_if_already_exists(
    db_connection,
    db_transaction,
    context,
    event,
    initial_user_without_guid_or_cognito_id,
    test_user_properties,
):
    """
    if the user has already been created but does not have a guid or a cognito user
    id then, it will be updated, and the guid / cognito user id will be populated.

    :param db_connection: _description_
    :type db_connection: _type_
    :param db_transaction: _description_
    :type db_transaction: _type_
    :param context: _description_
    :type context: _type_
    :param event: _description_
    :type event: _type_
    :param initial_user: _description_
    :type initial_user: _type_
    :param test_user_properties: _description_
    :type test_user_properties: _type_
    """
    test_idp_type_code = test_user_properties["idp_type_code"]
    test_idp_user_id = test_user_properties["idp_user_id"]
    test_cognito_user_id = test_user_properties["cognito_user_id"]
    test_idp_username = test_user_properties["idp_username"]

    # setup

    # execute
    result = lambda_function.lambda_handler(event, context)
    LOGGER.debug(f"result: \n{pprint.pformat(result, indent=4)}")

    # validate that there is one user in the database with the properties from
    # the incoming event
    cursor = db_connection.cursor()
    raw_query = """select count(*) from app_fam.fam_user where
        user_type_code = {} and
        user_guid = {} and
        cognito_user_id = {} and
        user_name = {};"""
    query = sql.SQL(raw_query).format(
        sql.Literal(test_idp_type_code),
        sql.Literal(test_idp_user_id),
        sql.Literal(test_cognito_user_id),
        sql.Literal(test_idp_username),
    )
    cursor.execute(query)

    count = cursor.fetchone()[0]

    assert count == 1


def test_single_parent_role_found(
    db_transaction,
    context,
    event,
    initial_user,
    create_test_fam_role,
    create_test_fam_cognito_client,
    create_user_role_xref_record,
    test_role_name,
):
    # execute
    result = lambda_function.lambda_handler(event, context)

    # validate that there is one user in the database with the properties from
    # the incoming event
    override_groups = result["response"]["claimsOverrideDetails"][
        "groupOverrideDetails"
    ]["groupsToOverride"]
    assert test_role_name in override_groups
