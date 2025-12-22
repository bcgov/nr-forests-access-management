import copy
import datetime
import logging
import os
import pprint
import sys
from zoneinfo import ZoneInfo

import pytest
from constant import TEST_ADMIN_ROLE_NAME, TEST_ROLE_NAME
from psycopg2 import sql

modulePath = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(modulePath)
import lambda_function  # noqa

LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
        "login_event_bceid.json",
        "login_event_bcsc.json",
        "login_event_bceid_min_attr.json",
        "login_event_bcsc_min_attr.json",
    ],
    indirect=True,
)
def test_create_user_if_not_found(
    db_pg_transaction, cognito_event, cognito_context, test_user_properties
):
    cursor = db_pg_transaction.cursor()

    # shorter variables
    test_idp_type_code = test_user_properties["idp_type_code"]
    test_idp_user_id = test_user_properties["idp_user_id"]
    test_cognito_user_id = test_user_properties["cognito_user_id"]
    test_idp_username = test_user_properties["idp_username"]
    test_idp_business_guid = test_user_properties["idp_business_id"]
    test_email = test_user_properties["email"]

    # make sure the user doesn't exist
    user_query = sql.SQL(
        """SELECT user_name from app_fam.fam_user where
            user_name = {0}"""
    ).format(sql.Literal(test_idp_username))

    cursor.execute(user_query)
    results = cursor.fetchall()
    LOGGER.debug(f"results: {results}")
    assert len(results) == 0
    assert results == []

    # simulate a login
    lambda_function.lambda_handler(cognito_event, cognito_context)

    # verify that the user exists now
    cursor.execute(user_query)
    results = cursor.fetchall()
    LOGGER.debug(f"results: {results}")
    assert len(results) == 1
    assert results[0][0] == test_idp_username

    # validate that there is one user in the database with primary properties from
    # the incoming event
    __verify_user_with_primary_attributes_found(
        db_pg_transaction,
        test_idp_type_code,
        test_idp_user_id,
        test_cognito_user_id,
        test_idp_username,
    )

    if test_idp_business_guid is not None:
        # validate the user is created with the business_guid
        __verify_user_with_optional_property_found(
            db_pg_transaction,
            test_idp_type_code,
            test_idp_user_id,
            test_cognito_user_id,
            test_idp_username,
            {"business_guid": test_idp_business_guid},
        )

    if test_email is not None:
        # validate the user is created with the test_email
        __verify_user_with_optional_property_found(
            db_pg_transaction,
            test_idp_type_code,
            test_idp_user_id,
            test_cognito_user_id,
            test_idp_username,
            {"email": test_email},
        )


@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
        "login_event_bceid.json",
        "login_event_bcsc.json",
        "login_event_bceid_min_attr.json",
        "login_event_bcsc_min_attr.json",
    ],
    indirect=True,
)
def test_update_user_if_already_exists(
    db_pg_transaction,
    cognito_event,
    cognito_context,
    test_user_properties,
    initial_user_without_guid_or_cognito_id,
):
    """
    if the user has already been created but does not have a guid or a cognito user
    id then, it will be updated, and the guid / cognito user id will be populated.
    """

    test_idp_type_code = test_user_properties["idp_type_code"]
    test_idp_user_id = test_user_properties["idp_user_id"]
    test_cognito_user_id = test_user_properties["cognito_user_id"]
    test_idp_username = test_user_properties["idp_username"]
    test_idp_business_guid = test_user_properties["idp_business_id"]
    test_email = test_user_properties["email"]

    # execute
    result = lambda_function.lambda_handler(cognito_event, cognito_context)
    LOGGER.debug(f"result: \n{pprint.pformat(result, indent=4)}")

    # validate that there is one user in the database with primary properties from
    # the incoming event
    __verify_user_with_primary_attributes_found(
        db_pg_transaction,
        test_idp_type_code,
        test_idp_user_id,
        test_cognito_user_id,
        test_idp_username,
    )

    cursor = db_pg_transaction.cursor()
    if test_idp_business_guid is not None:
        # verify the user is updated with business_guid
        __verify_user_with_optional_property_found(
            db_pg_transaction,
            test_idp_type_code,
            test_idp_user_id,
            test_cognito_user_id,
            test_idp_username,
            {"business_guid": test_idp_business_guid},
        )

    if test_email is not None:
        # verify the user is updated with business_guid
        __verify_user_with_optional_property_found(
            db_pg_transaction,
            test_idp_type_code,
            test_idp_user_id,
            test_cognito_user_id,
            test_idp_username,
            {"email": test_email},
        )

def __verify_user_with_primary_attributes_found(
    db_pg_transaction,
    test_idp_type_code,
    test_idp_user_id,
    test_cognito_user_id,
    test_idp_username,
):
    cursor = db_pg_transaction.cursor()
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


def __verify_user_with_optional_property_found(
    db_pg_transaction,
    test_idp_type_code,
    test_idp_user_id,
    test_cognito_user_id,
    test_idp_username,
    optional_key_value: dict,
):
    cursor = db_pg_transaction.cursor()
    key, value = list(optional_key_value.items())[0]  # Extract the key and value from the dictionary
    raw_query = f"""select count(*) from app_fam.fam_user where
        user_type_code = {{}} and
        user_guid = {{}} and
        cognito_user_id = {{}} and
        user_name = {{}} and
        {key} = {{}};"""

    query = sql.SQL(raw_query).format(
        sql.Literal(test_idp_type_code),
        sql.Literal(test_idp_user_id),
        sql.Literal(test_cognito_user_id),
        sql.Literal(test_idp_username),
        sql.Literal(value),
    )

    cursor.execute(query)
    count = cursor.fetchone()[0]
    assert count == 1


@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
        "login_event_bceid.json",
        "login_event_bcsc.json",
        "login_event_bceid_min_attr.json",
        "login_event_bcsc_min_attr.json",
    ],
    indirect=True,
)
def test_direct_role_assignment(
    db_pg_transaction,
    cognito_event,
    cognito_context,
    initial_user,
    create_test_fam_role,
    create_test_fam_cognito_client,
    create_user_role_xref_record,
    create_fam_application_admin_record,
):
    """role doesn't have childreen (ie no forest client roles associated
    and the user is getting assigned directly to the role"""

    # setup user-role assignment
    create_test_fam_role()
    create_user_role_xref_record()
    # execute
    result = lambda_function.lambda_handler(cognito_event, cognito_context)

    # validate that there is one user in the database with the properties from
    # the incoming event
    override_groups = result["response"]["claimsAndScopeOverrideDetails"][
        "groupOverrideDetails"
    ]["groupsToOverride"]
    LOGGER.debug(f"override groups: {override_groups}")
    assert TEST_ROLE_NAME in override_groups
    assert TEST_ADMIN_ROLE_NAME in override_groups


@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
        "login_event_bceid.json",
        "login_event_bcsc.json",
        "login_event_bceid_min_attr.json",
        "login_event_bcsc_min_attr.json",
    ],
    indirect=True,
)
def test_parent_role_assignment(
    db_pg_transaction,
    cognito_event,
    cognito_context,
    initial_user,
    create_test_fam_cognito_client,
    create_fam_child_parent_role_assignment,
    create_user_role_xref_record,
):
    """if set up as a fom submitter for a specific forest client, then you are assigned
    to the child role that has a forest client
    """

    # setup user-role assignment
    create_user_role_xref_record()
    result = lambda_function.lambda_handler(cognito_event, cognito_context)
    groups = result["response"]["claimsAndScopeOverrideDetails"]["groupOverrideDetails"][
        "groupsToOverride"
    ]
    LOGGER.debug(f"result: {groups}")
    assert len(groups) == 1
    assert groups[0] == TEST_ROLE_NAME


@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
        "login_event_bceid.json",
        "login_event_bcsc.json",
        "login_event_bceid_min_attr.json",
        "login_event_bcsc_min_attr.json",
    ],
    indirect=True,
)
def test_new_user_has_no_roles(db_pg_transaction, cognito_event, cognito_context):
    """runs against a database that contains only data that has been injected
    by the migrations.  Should not contain any roles in the result
    """
    result = lambda_function.lambda_handler(cognito_event, cognito_context)
    groups = result["response"]["claimsAndScopeOverrideDetails"]["groupOverrideDetails"][
        "groupsToOverride"
    ]
    LOGGER.debug(f"groups: {groups}")
    assert groups == []


@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
        "login_event_bceid.json",
        "login_event_bcsc.json",
        "login_event_bceid_min_attr.json",
        "login_event_bcsc_min_attr.json",
    ],
    indirect=True,
)
def test_exception_with_wrong_cognito_event(
    db_pg_transaction, cognito_event, cognito_context
):
    """
    if runs into any problem or errors, can catch the exception and print in the log
    """
    temp_cognito_event = copy.deepcopy(cognito_event)
    del temp_cognito_event["callerContext"]
    with pytest.raises(Exception) as exc:
        lambda_function.lambda_handler(temp_cognito_event, cognito_context)
    assert exc is not None


# --- Expiry Logic Tests ---
@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
    ],
    indirect=True,
)
def test_expired_role_not_returned(
    db_pg_transaction,
    cognito_event,
    cognito_context,
    initial_user,
    create_test_fam_role,
    create_test_fam_cognito_client,
    create_user_role_xref_record,
):
    # Assign role with expiry_date in the past
    bc_tz = ZoneInfo("America/Vancouver")
    expired_date = datetime.datetime.now(bc_tz) - datetime.timedelta(days=5)
    create_test_fam_role()
    create_user_role_xref_record(expiry_date=expired_date)
    result = lambda_function.lambda_handler(cognito_event, cognito_context)
    groups = result["response"]["claimsAndScopeOverrideDetails"]["groupOverrideDetails"]["groupsToOverride"]
    assert TEST_ROLE_NAME not in groups


@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
    ],
    indirect=True,
)
def test_non_expired_role_returned(
    db_pg_transaction,
    cognito_event,
    cognito_context,
    initial_user,
    create_test_fam_role,
    create_test_fam_cognito_client,
    create_user_role_xref_record,
):
    # Assign role with expiry_date in the future
    bc_tz = ZoneInfo("America/Vancouver")
    future_date = datetime.datetime.now(bc_tz) + datetime.timedelta(days=1)
    create_test_fam_role()
    create_user_role_xref_record(expiry_date=future_date)
    result = lambda_function.lambda_handler(cognito_event, cognito_context)
    groups = result["response"]["claimsAndScopeOverrideDetails"]["groupOverrideDetails"]["groupsToOverride"]
    assert TEST_ROLE_NAME in groups

@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
    ],
    indirect=True,
)
def test_null_expiry_role_returned(
    db_pg_transaction,
    cognito_event,
    cognito_context,
    initial_user,
    create_test_fam_role,
    create_test_fam_cognito_client,
    create_user_role_xref_record,
):
    # Assign role with expiry_date=None (should be returned)
    create_test_fam_role()
    create_user_role_xref_record(expiry_date=None)
    result = lambda_function.lambda_handler(cognito_event, cognito_context)
    groups = result["response"]["claimsAndScopeOverrideDetails"]["groupOverrideDetails"]["groupsToOverride"]
    assert TEST_ROLE_NAME in groups

@pytest.mark.parametrize(
    "cognito_event",
    [
        "login_event.json",
    ],
    indirect=True,
)
def test_mixed_expiry_roles(
    db_pg_transaction,
    cognito_event,
    cognito_context,
    initial_user,
    create_test_fam_role,
    create_test_fam_cognito_client,
    create_user_role_xref_record,
):
    bc_tz = ZoneInfo("America/Vancouver")
    expired_date = datetime.datetime.now(bc_tz) - datetime.timedelta(days=1)
    future_date = datetime.datetime.now(bc_tz) + datetime.timedelta(days=1)
    expired_role_name = TEST_ROLE_NAME + "_EXPIRED"
    # Create expired role in DB
    create_test_fam_role(role_name=expired_role_name)
    # Create valid role in DB
    create_test_fam_role()
    # Assign expired role to user
    create_user_role_xref_record(role_name=expired_role_name, expiry_date=expired_date)
    # Assign valid role to user
    create_user_role_xref_record(role_name=TEST_ROLE_NAME, expiry_date=future_date)

    result = lambda_function.lambda_handler(cognito_event, cognito_context)
    groups = result["response"]["claimsAndScopeOverrideDetails"]["groupOverrideDetails"]["groupsToOverride"]
    assert TEST_ROLE_NAME in groups
    assert expired_role_name not in groups


    @pytest.mark.parametrize(
        "cognito_event",
        [
            "login_event.json",
        ],
        indirect=True,
    )
    def test_today_expiry_role_returned(
        db_pg_transaction,
        cognito_event,
        cognito_context,
        initial_user,
        create_test_fam_role,
        create_test_fam_cognito_client,
        create_user_role_xref_record,
    ):
        # Assign role with expiry_date set to today (should be returned)
        bc_tz = ZoneInfo("America/Vancouver")
        now = datetime.datetime.now(bc_tz)
        create_test_fam_role()
        create_user_role_xref_record(expiry_date=now)
        result = lambda_function.lambda_handler(cognito_event, cognito_context)
        groups = result["response"]["claimsAndScopeOverrideDetails"]["groupOverrideDetails"]["groupsToOverride"]
        assert TEST_ROLE_NAME in groups
