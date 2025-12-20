import functools
import json
import logging
import logging.config
import os
from enum import Enum
from typing import Any

import config
import event_type
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection

# seeing as a simple lambda function, use a simple fileconfig for the audit logging
# config, and setting up manually if the function is called directly
# as is done when lambda calls this script.
# ... see end of file

logConfigFile = os.path.join(os.path.dirname(__file__), "./config", "logging.config")
logging.config.fileConfig(logConfigFile, disable_existing_loggers=False)

LOGGER = logging.getLogger()
LOGLEVEL = os.getenv("LOGLEVEL_AUTH", "INFO").upper() # Used to trun "DEBUG" logging on/off; default to "INFO"
LOGGER.setLevel(LOGLEVEL)

IDP_NAME_BCSC_DEV = "ca.bc.gov.flnr.fam.dev"
IDP_NAME_BCSC_TEST = "ca.bc.gov.flnr.fam.test"
IDP_NAME_BCSC_PROD = "ca.bc.gov.flnr.fam.prod"
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
    IDP_NAME_BCSC_PROD: USER_TYPE_BCSC_PROD,
}


class AuditEventOutcome(str, Enum):
    SUCCESS = 1
    FAIL = 0


def audit_log(original_func):
    """
    Decorator to handle audit log for lambda_handler (AWS Cognito Pre-Token tirgger event) function.
    Please refer to below for why "@functools.wraps" Python decorator is used.:
        ref: https://hayageek.com/functools-wraps-in-python/#:~:text=The%20functools.,in%20every%20way%20that%20matters. and
        ref: Ref: https://docs.python.org/3/library/functools.html#functools.wraps
    """
    @functools.wraps(original_func)
    def decorated_func(*args, **kwargs):
        audit_event_log = {
            "auditEventTypeCode": "USER_LOGIN",
            "auditEventResultCode": AuditEventOutcome.SUCCESS.name,
            "requestingUser": {},
        }

        try:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            LOGGER.debug(f"function {original_func.__name__} called with args {signature}")

            event = args[0]  # First argument is the event
            audit_event_log["cognitoApplicationId"] = event["callerContext"]["clientId"]
            audit_event_log["requestingUser"]["userGuid"] = event["request"]["userAttributes"]["custom:idp_user_id"]
            audit_event_log["requestingUser"]["userType"] = USER_TYPE_CODE_DICT[
                event["request"]["userAttributes"]["custom:idp_name"]
            ]

            if audit_event_log["requestingUser"]["userType"] == USER_TYPE_IDIR:
                audit_event_log["requestingUser"]["idpUserName"] = event["request"]["userAttributes"][
                    "custom:idp_username"]
            elif audit_event_log["requestingUser"]["userType"] == USER_TYPE_BCEID_BUSINESS:
                audit_event_log["requestingUser"]["idpUserName"] = event["request"]["userAttributes"][
                    "custom:idp_username"]
                audit_event_log["requestingUser"]["businessGuid"] = event["request"][
                    "userAttributes"].get("custom:idp_business_id")
            else:
                # for bc service card login, there is no custom:idp_username mapped, use display name instead, and it is optinal
                audit_event_log["requestingUser"]["idpDisplayName"] = event["request"][
                    "userAttributes"].get("custom:idp_display_name")

            audit_event_log["requestingUser"]["cognitoUsername"] = event["userName"]

            func_return = original_func(*args, **kwargs)

            # original_function execution was successful, log the change in Cognito event 'groupsToOverride' for user's access roles.
            audit_event_log["requestingUser"]["accessRoles"] = func_return["response"]["claimsOverrideDetails"][
                "groupOverrideDetails"]["groupsToOverride"]

            return func_return

        except Exception as e:
            audit_event_log["auditEventResultCode"] = AuditEventOutcome.FAIL.name
            audit_event_log["exception"] = original_func.__name__ + ": " + str(e)
            raise e

        finally:
            LOGGER.info(json.dumps(audit_event_log))

    return decorated_func


@audit_log
def lambda_handler(event: event_type.Event, context: Any) -> event_type.Event:
    """recieves a cognito event object, checks to see if the user associated
    with the event exists in the database. If not it gets added. Finally
    the roles associated with the user are retrieved and used to populate the
    cognito event objects property.

    :param event: the cognito event
    :type event: event_type.Event
    :param context: context sent by cognito, not used by the function
    :type context: Any
    :return: returns a modified event with the roles injected into it
    :rtype: event_type.Event

    When we onboard applications to FAM, we config at least the minimum attribute list for them
    All applications should be configured with user attributes: "custom:idp_name", "custom:idp_user_id", "custom:idp_username"
    """
    LOGGER.debug(f"context: {context}")
    LOGGER.debug(f"event - {event.get("version", "V1_0")}: {event}")

    db_connection = obtain_db_connection()
    populate_user_if_necessary(db_connection, event)

    event_with_authz = handle_event(db_connection, event)

    release_db_connection(db_connection)
    return event_with_authz


def obtain_db_connection() -> Any:
    db_connection_string = config.get_db_connection_string()
    db_connection = psycopg2.connect(db_connection_string, sslmode="disable")
    db_connection.autocommit = False
    return db_connection


def release_db_connection(db_connection):
    db_connection.commit()
    db_connection.close()


def populate_user_if_necessary(db_connection, event) -> None:
    """Checks to see if a user described in the input cognito event exists
    in the authZ database.  If the user does not exist then the user is
    added to the database"""

    user_type = event["request"]["userAttributes"]["custom:idp_name"]
    user_guid = event["request"]["userAttributes"]["custom:idp_user_id"]
    business_guid = event["request"]["userAttributes"].get(
        "custom:idp_business_id"
    )  # only bceid user has this attribute
    cognito_user_id = event["userName"]
    email = event["request"]["userAttributes"].get("email")
    user_type_code = USER_TYPE_CODE_DICT[user_type]

    if user_type_code in [USER_TYPE_BCSC_DEV, USER_TYPE_BCSC_TEST, USER_TYPE_BCSC_PROD]:
        user_name = user_guid
    else:
        user_name = event["request"]["userAttributes"]["custom:idp_username"]

    LOGGER.debug(f"'populate_user_if_necessary': (user_name: {user_name}, user_type_code: {user_type_code}, "
                 f"user_guid: {user_guid}, business_guid: {business_guid}, email: {email})")

    cursor = db_connection.cursor()

    # in the case of historical FAM user that has no user_guid stored, add their user_guid
    # if user does not exist or user has a user_guid already, this update query will do nothing
    query_add_guid= """
        UPDATE app_fam.fam_user SET
        user_guid={user_guid}
        WHERE user_type_code={user_type_code}
        and LOWER(user_name)={user_name}
        and user_guid is null
    """
    sql_query_query_add_guid = sql.SQL(query_add_guid).format(
        user_guid=sql.Literal(user_guid),
        user_type_code=sql.Literal(user_type_code),
        user_name=sql.Literal(user_name.lower()),
    )
    cursor.execute(sql_query_query_add_guid)

    # insert new user, or update user information
    raw_query = """INSERT INTO app_fam.fam_user
        (user_type_code, user_guid, cognito_user_id, user_name, business_guid, email,
        create_user, create_date, update_user, update_date)
        VALUES( {user_type_code}, {user_guid}, {cognito_user_id}, {user_name}, {business_guid}, {email},
        CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE)
        ON CONFLICT (user_type_code, user_guid) DO
        UPDATE SET user_name = {user_name},  cognito_user_id = {cognito_user_id}, business_guid = {business_guid}, email = {email}, update_user = CURRENT_USER, update_date = CURRENT_DATE;"""

    sql_query = sql.SQL(raw_query).format(
        user_type_code=sql.Literal(user_type_code),
        user_guid=sql.Literal(user_guid),
        cognito_user_id=sql.Literal(cognito_user_id),
        user_name=sql.Literal(user_name),
        business_guid=sql.Literal(business_guid),
        email=sql.Literal(email),
    )

    cursor.execute(sql_query)


def handle_event(db_connection, event) -> event_type.Event:
    # Currently, only access token customization is needed.
    event = access_token_groups_override(db_connection, event)
    event = access_token_custom_claims_override(event)

    return event


def access_token_groups_override(db_connection: connection, event: event_type.Event) -> event_type.Event:
    """ Custom user groups to be added to access token.

    In AWS Lambda version V2_0, the property to override in the response object for groups is:
    - claimsAndScopeOverrideDetails.groupOverrideDetails.groupsToOverride
    - ref: https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html

    :param db_connection: Database connection object
    :param event: The cognito event
    :return: Updated event with groups overridden
    """
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
            AND (role_assignment.expiry_date IS NULL OR role_assignment.expiry_date >= CURRENT_TIMESTAMP)
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

    sql_query = sql.SQL(query).format(
        user_guid=sql.Literal(user_guid),
        user_type_code=sql.Literal(user_type_code),
        cognito_client_id=sql.Literal(cognito_client_id),
    )

    cursor.execute(sql_query)
    role_list = []
    for record in cursor:
        role_list.append(record[0])

    # check if login through FAM
    query_application = """
    SELECT application.application_name
    FROM app_fam.fam_application application
        JOIN app_fam.fam_application_client client ON
            application.application_id = client.application_id
    WHERE
        client.cognito_client_id = {cognito_client_id};
    """
    sql_query_application = sql.SQL(query_application).format(
        cognito_client_id=sql.Literal(cognito_client_id),
    )
    cursor.execute(sql_query_application)
    # if login through FAM, check fam app admin and add to role list
    for record in cursor:
        if record[0] == "FAM":
            query_fam_app_admin = """
            SELECT application.application_name
            FROM app_fam.fam_application_admin app_admin
                INNER JOIN app_fam.fam_application application ON
                    app_admin.application_id = application.application_id
                JOIN app_fam.fam_user fam_user ON
                    app_admin.user_id = fam_user.user_id
            WHERE
                fam_user.user_guid = {user_guid}
                AND fam_user.user_type_code = {user_type_code};
            """
            sql_query_fam_app_admin = sql.SQL(query_fam_app_admin).format(
                user_guid=sql.Literal(user_guid),
                user_type_code=sql.Literal(user_type_code),
            )
            cursor.execute(sql_query_fam_app_admin)
            for record in cursor:
                role_list.append(f"{record[0]}_ADMIN")

    claimsAndScopeOverrideDetails = event["response"].get("claimsAndScopeOverrideDetails", {})
    if "groupOverrideDetails" not in claimsAndScopeOverrideDetails:
        claimsAndScopeOverrideDetails["groupOverrideDetails"] = {
            "groupsToOverride": role_list,
            "iamRolesToOverride": [],
            "preferredRole": ""
        }
    else:
        claimsAndScopeOverrideDetails["groupOverrideDetails"]["groupsToOverride"] = role_list

    event["response"]["claimsAndScopeOverrideDetails"] = claimsAndScopeOverrideDetails

    LOGGER.debug(f"'access_token_groups_override' user's access roles are appended for the token: (access roles: {role_list}).")
    return event


def access_token_custom_claims_override(event: event_type.Event) -> event_type.Event:
    """ Custom user attributes to be added to access token.
    In AWS Lambda version V2_0, the property to override in the response object from custom claims is:
    - claimsAndScopeOverrideDetails.accessTokenGeneration.claimsToAddOrOverride
    - ref: https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html

    :param event ('event_type.Event'): the cognito event
    :return ('event_type.Event'): returns the event as is
    """
    # Extract custom user attributes
    idp_username = event["request"]["userAttributes"]["custom:idp_username"]
    idp_name = event["request"]["userAttributes"]["custom:idp_name"]

    claimsAndScopeOverrideDetails = event["response"].get("claimsAndScopeOverrideDetails", {})
    if "accessTokenGeneration" not in claimsAndScopeOverrideDetails:
        claimsAndScopeOverrideDetails["accessTokenGeneration"] = {
            "claimsToAddOrOverride": {
                "custom:idp_username": idp_username,
                "custom:idp_name": idp_name
            }
        }
    else:
        claimsAndScopeOverrideDetails["accessTokenGeneration"]["claimsToAddOrOverride"] = {
            "custom:idp_username": idp_username,
            "custom:idp_name": idp_name
        }

    event["response"]["claimsAndScopeOverrideDetails"] = claimsAndScopeOverrideDetails

    return event