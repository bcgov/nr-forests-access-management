import os
import logging
import psycopg2
import pprint
import config
import event_type
from typing import List, Dict, TypedDict, Any, Union


# seeing as a simple lambda function, not using a fileconfig for the logging
# config, and instead setting up manually if the function is called directly
# as is done when lambda calls this script.
# ... see end of file
LOGGER = logging.getLogger()


def lambda_handler(event: event_type.Event, context: Any):
    LOGGER.debug(f"context: {context}")
    authZ = AuthorizationQuery(event)
    event_with_authZ = authZ.lambda_handler()
    return event_with_authZ


class AuthorizationQuery(object):
    db_connection = None
    testing = False

    def __init__(self, event: event_type.Event, testing: bool = False):
        self.user_type_code_dict = {"idir": "I", "bceidbusiness": "B"}
        self.testing = testing
        self.event = event
        self.obtain_db_connection()

    def obtain_db_connection(self):
        if self.db_connection is None:
            db_connection_string = config.get_db_connection_string()
            self.db_connection = psycopg2.connect(
                db_connection_string, sslmode="disable"
            )
            self.db_connection.autocommit = False

    def release_db_connection(self):
        if not self.testing:
            self.db_connection.commit()
            self.db_connection.close()

    def lambda_handler(self):
        """ """
        pp = pprint.PrettyPrinter(indent=4, width=1)
        envStr = pp.pformat(dict(os.environ))
        LOGGER.debug(f"## ENVIRONMENT VARIABLES\n {envStr}")
        LOGGER.debug(f"## EVENT\n {pp.pformat(self.event)}")

        # could just do the db connection when obj is instantiated
        self.obtain_db_connection()

        self.populate_user_if_necessary()

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

        # query_result = cursor.fetchone()
        # app_description = query_result[0]

        self.release_db_connection()

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

    def populate_user_if_necessary(self):
        """ """

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


if __name__ == '__main__':
    LOGGER = logging.getLogger(__name__)
    # TODO: Leave at debug for initial deploy, then go to INFO
    #       once working
    LOGGER.setLevel(logging.DEBUG)  # logging.INFO
    hndlr = logging.StreamHandler()
    # add line number to format
    logFormat = '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d -' + \
                ' %(message)s'
    formatter = logging.Formatter(logFormat)
    hndlr.setFormatter(formatter)
    LOGGER.addHandler(hndlr)
