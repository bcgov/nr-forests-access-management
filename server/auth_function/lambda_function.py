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
    authZ = AuthorizationQuery(event)
    authZ.populate_user_if_necessary()
    event_with_authZ = authZ.lambda_handler()
    authZ.release_db_connection()
    return event_with_authZ


class AuthorizationQuery(object):
    db_connection = None
    testing = False

    # testing: bool = False
    def __init__(self, event: event_type.Event) -> None:
        self.user_type_code_dict = {"idir": "I", "bceidbusiness": "B"}
        # self.testing = testing
        self.event = event
        self.obtain_db_connection()

    def obtain_db_connection(self) -> None:
        """checks to see if a database connection exists, and if it does not
        then creates one.
        """
        if self.db_connection is None:
            db_connection_string = config.get_db_connection_string()
            self.db_connection = psycopg2.connect(
                db_connection_string, sslmode="disable"
            )
            self.db_connection.autocommit = False

    def release_db_connection(self) -> None:
        """closing the database connection
        """
        self.db_connection.close()

    def lambda_handler(self) -> event_type.Event:
        """Queries the auth database for the roles associated with the user
        that is described in the cognito event, the function then populates
        the roles into the event object and returns it."""
        # could just do the db connection when obj is instantiated
        self.obtain_db_connection()

        cursor = self.db_connection.cursor()
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
        user_guid = self.event["request"]["userAttributes"]["custom:idp_user_id"]
        user_type_code = self.user_type_code_dict[
            self.event["request"]["userAttributes"]["custom:idp_name"]
        ]
        cognito_client_id = self.event["callerContext"]["clientId"]

        sql_query = psycopg2.sql.SQL(query).format(
            user_guid=psycopg2.sql.Literal(user_guid),
            user_type_code=psycopg2.sql.Literal(user_type_code),
            cognito_client_id=psycopg2.sql.Literal(cognito_client_id),
        )

        cursor.execute(sql_query)
        roleList = []
        for record in cursor:
            roleList.append(record[0])

        self.event["response"]["claimsOverrideDetails"] = {
            "groupOverrideDetails": {
                "groupsToOverride": roleList,
                "iamRolesToOverride": [],
                "preferredRole": "",
            }
        }
        # might want to not return...  just have the call retrieve it from
        # the property obj.event
        return self.event

    def populate_user_if_necessary(self) -> None:
        """ Checks to see if a user described in the input cognito event exists
        in the authZ database.  If the user does not exist then the user is
        added to the database"""

        user_type = self.event["request"]["userAttributes"]["custom:idp_name"]
        user_guid = self.event["request"]["userAttributes"]["custom:idp_user_id"]
        cognito_user_id = self.event["userName"]
        user_name = self.event["request"]["userAttributes"]["custom:idp_username"]

        user_type_code_dict = {"idir": "I", "bceidbusiness": "B"}
        user_type_code = user_type_code_dict[user_type]

        raw_query = """INSERT INTO app_fam.fam_user
            (user_type_code, user_guid, cognito_user_id, user_name,
            create_user, create_date, update_user, update_date)
            VALUES( {user_type_code}, {user_guid}, {cognito_user_id}, {user_name},
            CURRENT_USER, CURRENT_DATE, CURRENT_USER, CURRENT_DATE)
            ON CONFLICT ON CONSTRAINT fam_usr_uk DO
            UPDATE SET user_guid = {user_guid},  cognito_user_id = {cognito_user_id};"""

        sql_query = psycopg2.sql.SQL(raw_query).format(
            user_type_code=psycopg2.sql.Literal(user_type_code),
            user_guid=psycopg2.sql.Literal(user_guid),
            cognito_user_id=psycopg2.sql.Literal(cognito_user_id),
            user_name=psycopg2.sql.Literal(user_name),
        )

        self.db_connection.cursor().execute(sql_query)
        self.db_connection.commit()


if __name__ == "__main__":
    # Setting up the logging for when the function is integrated into AWS as a
    # lambda and called by cognito
    LOGGER = logging.getLogger(__name__)
    # TODO: Leave at debug for initial deploy, then go to INFO
    #       once working
    LOGGER.setLevel(logging.INFO)  # logging.INFO
    hndlr = logging.StreamHandler()
    # add line number to format
    logFormat = "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d -" + " %(message)s"
    formatter = logging.Formatter(logFormat)
    hndlr.setFormatter(formatter)
    LOGGER.addHandler(hndlr)
