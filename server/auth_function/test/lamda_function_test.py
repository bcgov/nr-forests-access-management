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
    auth_object, test_user_properties
):
    """
    test to make sure that if the user doesn't exist in the database it will
    be created.

    :param db_connection: _description_
    :type db_connection: _type_
    :param db_transaction: _description_
    :type db_transaction: _type_
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
    auth_object.lambda_handler()

    # validate that there is one user in the database with the properties from
    # the incoming event
    cursor = auth_object.db_connection.cursor()

    raw_query = """select count(*) from app_fam.fam_user where
        user_type_code = {} and
        user_guid = {} and
        cognito_user_id = {} and
        user_name = {};"""

    # potentially another way to handle params:
    #   https://www.psycopg.org/psycopg3/docs/basic/params.html
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
    auth_object,
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
    result = auth_object.lambda_handler()
    LOGGER.debug(f"result: \n{pprint.pformat(result, indent=4)}")

    # validate that there is one user in the database with the properties from
    # the incoming event
    cursor = auth_object.db_connection.cursor()
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


def test_direct_role_assignment(
    auth_object,
    initial_user,
    create_test_fam_role,
    create_test_fam_cognito_client,
    create_user_role_xref_record,
    test_role_name,
):
    """ role doesn't have childreen (ie no forest client roles associated
    and the user is getting assigned directly to the role"""
    # execute
    result = auth_object.lambda_handler()

    # validate that there is one user in the database with the properties from
    # the incoming event
    override_groups = result["response"]["claimsOverrideDetails"][
        "groupOverrideDetails"
    ]["groupsToOverride"]
    assert test_role_name in override_groups


def test_parent_role_assignment(auth_object,
                                initial_user,
                                create_fam_child_parent_role_assignment,
                                create_user_role_xref_record):
    """ if set up as a fom submitter for a specific forest client, then you are assigned
    to the child role that has a forest client

    auth_object - the lambda function that queries database for authorization
    initial_user - creates an initial user that will be used for the test
    create_fam_child_parent_role_assignment - Creates two roles, an abstract
        'A' type role, and a 'C' role that is a parent of the abstract role



    """
    #auth_object.lambda_handler(event,)
    assert True
    result = auth_object.lambda_handler()
    groups = result["response"]["claimsOverrideDetails"][
        "groupOverrideDetails"
    ]["groupsToOverride"]
    LOGGER.debug(f"result: {groups}")
    pass

# next some sad case scenarios / db fails / roles not found / multiple roles found for user
# login with user but wrong user is setup.
#   -