import logging
import psycopg2
import psycopg2.sql
import config
import event_type
from typing import Any


# seeing as a simple lambda function, not using a fileconfig for the logging
# config, and instead setting up manually if the function is called directly
# as is done when lambda calls this script.
# ... see end of file
LOGGER = logging.getLogger()

IDP_NAME_BCSC_DEV = "ca.bc.gov.flnr.fam.dev"
IDP_NAME_BCSC_TEST = "ca.bc.gov.flnr.fam.test"
IDP_NAME_BCSC_PROD = "ca.bc.gov.flnr.fam"
IDP_NAME_IDIR = "idir"
IDP_NAME_BCEID_BUSINESS = "bceidbusiness"

USER_TYPE_IDIR = "I"
USER_TYPE_BCEID_BUSINESS = "B"
USER_TYPE_BCSC_DEV = "CD"
USER_TYPE_BCSC_TEST = "CT"
USER_TYPE_BCSC_PROD = "CP"

USER_TYPE_CODE_DICT = {
    IDP_NAME_IDIR: USER_TYPE_IDIR,
    IDP_NAME_BCEID_BUSINESS: USER_TYPE_BCEID_BUSINESS,
    IDP_NAME_BCSC_DEV: USER_TYPE_BCSC_DEV,
    IDP_NAME_BCSC_TEST: USER_TYPE_BCSC_TEST,
    IDP_NAME_BCSC_PROD: USER_TYPE_BCSC_PROD
}


def lambda_handler(event: event_type.Event, context: Any) -> event_type.Event:
    """recieves a cognito event object, checks to see if the user associated
    with the event exists in the database.  If not it gets added.  Finally
    the roles associated with the user are retrieved and used to populate the
    cognito event objects property:

    response.claimsOverrideDetails.groupOverrideDetails {
        groupsToOverride: [<role are injected here>]
        iamRolesToOverride: [],
        preferredRole": ""
    }

    :param event: the cognito event
    :type event: event_type.Event
    :param context: context sent by cognito, not used by the function
    :type context: Any
    :return: returns a modified event with the roles injected into it
    :rtype: event_type.Event
    """
    LOGGER.debug(f"context: {context}")

    db_connection = obtain_db_connection()
    populate_user_if_necessary(db_connection, event)

    event_with_authz = handle_event(db_connection, event)

    release_db_connection(db_connection)

    return event_with_authz


def obtain_db_connection() -> Any:
    db_connection_string = config.get_db_connection_string()
    db_connection = psycopg2.connect(
        db_connection_string, sslmode="disable"
    )
    db_connection.autocommit = False
    return db_connection


def release_db_connection(db_connection):
    db_connection.commit()
    db_connection.close()


def populate_user_if_necessary(db_connection, event) -> None:
    """ Checks to see if a user described in the input cognito event exists
    in the authZ database.  If the user does not exist then the user is
    added to the database"""

    user_type = event["request"]["userAttributes"]["custom:idp_name"]
    user_guid = event["request"]["userAttributes"]["custom:idp_user_id"]
    cognito_user_id = event["userName"]

    user_type_code = USER_TYPE_CODE_DICT[user_type]

    if user_type_code in [USER_TYPE_BCSC_DEV, USER_TYPE_BCSC_TEST, USER_TYPE_BCSC_PROD]:
        user_name = user_guid
    else:
        user_name = event["request"]["userAttributes"]["custom:idp_username"]

    raw_query = """INSERT INTO app_fam.fam_user
        (user_type_code, user_guid, cognito_user_id, user_name,
        create_user, create_date, update_user, update_date)
        VALUES( {user_type_code}, {user_guid}, {cognito_user_id}, {user_name},
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE)
        ON CONFLICT (user_type_code, lower(user_name)) DO
        UPDATE SET user_guid = {user_guid},  cognito_user_id = {cognito_user_id};"""

    sql_query = psycopg2.sql.SQL(raw_query).format(
        user_type_code=psycopg2.sql.Literal(user_type_code),
        user_guid=psycopg2.sql.Literal(user_guid),
        cognito_user_id=psycopg2.sql.Literal(cognito_user_id),
        user_name=psycopg2.sql.Literal(user_name),
    )

    db_connection.cursor().execute(sql_query)


def handle_event(db_connection, event) -> event_type.Event:
    """Queries the auth database for the roles associated with the user
    that is described in the cognito event, the function then populates
    the roles into the event object and returns it."""

    cursor = db_connection.cursor()
    query = """
    SELECT
        role.role_name,
        role.client_number_id,
        parent_role.role_name as parent_role
    FROM app_fam.fam_role role
        LEFT JOIN app_fam.fam_role parent_role ON
            role.parent_role_id = parent_role.role_id
        INNER JOIN app_fam.fam_application application ON
            role.application_id = application.application_id
        JOIN app_fam.fam_application_client client ON
            application.application_id = client.application_id
        JOIN app_fam.fam_user_role_xref role_assignment ON
            role.role_id = role_assignment.role_id
        JOIN app_fam.fam_user user_assigned ON
            role_assignment.user_id = user_assigned.user_id
    WHERE
        user_assigned.user_guid = {user_guid}
        AND user_assigned.user_type_code = {user_type_code}
        AND client.cognito_client_id = {cognito_client_id};
    """
    user_guid = event["request"]["userAttributes"]["custom:idp_user_id"]
    user_type_code = USER_TYPE_CODE_DICT[
        event["request"]["userAttributes"]["custom:idp_name"]
    ]
    cognito_client_id = event["callerContext"]["clientId"]

    sql_query = psycopg2.sql.SQL(query).format(
        user_guid=psycopg2.sql.Literal(user_guid),
        user_type_code=psycopg2.sql.Literal(user_type_code),
        cognito_client_id=psycopg2.sql.Literal(cognito_client_id),
    )

    cursor.execute(sql_query)
    role_list = []
    for record in cursor:
        role_list.append(record[0])

    event["response"]["claimsOverrideDetails"] = {
        "groupOverrideDetails": {
            "groupsToOverride": role_list,
            "iamRolesToOverride": [],
            "preferredRole": "",
        }
    }
    return event

# Junk commit
