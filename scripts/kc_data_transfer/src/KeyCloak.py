import logging
import requests
import constants


LOGGER = logging.getLogger(__name__)
APP_JSON = "application/json"


class KeycloakWrapper:
    """
    most of this code is just lifted from the fom user repo
    """

    def __init__(self):
        self.get_access_token()
        self.default_headers = {"Authorization": "Bearer " + self.access_token}
        self.kc_realm_url = (
            f"{constants.KC_HOST}/auth/admin/realms/{constants.KC_REALM}"
        )

    def get_access_token(self):
        """using client id and secret queries keycloak for access token"""
        uri = (
            f"{constants.KC_HOST}/auth/realms/{constants.KC_REALM}"
            + "/protocol/openid-connect/token"
        )
        header = {"Accept": APP_JSON}
        params = {
            "client_id": constants.KC_CLIENTID,
            "client_secret": constants.KC_SECRET,
            "grant_type": "client_credentials",
        }
        LOGGER.debug(f"uri: {uri}")
        r = requests.post(uri, data=params, headers=header)
        r.raise_for_status()
        access_key = r.json()
        self.access_token = access_key["access_token"]
        LOGGER.debug(f"response as json string {self.access_token}")

    def get_matching_users(self, user_id, user_and_email_only=True):
        """Keycloak contains a lot of information about users.  This method
        determines if a user_id exists in keycloak.  The method will do its own
        search of all the users in keycloak.  (not efficient)

        Looks for either <user_id>@<identity provider>, or looks for any user id
        that matches the identity provider.

        If more than one user is found then a warning message will be logged.

            user@dir
            user@bceid
            <email address>

        Will get a list of the users in the realm and search for

        :param user_id: [description]
        :type user_id: [type]
        :return: [description]
        :rtype: [type]
        """
        users = self.get_all_users()
        matched_users = []
        LOGGER.debug(f"user_id: {user_id}")
        for user in users:
            user_match = False
            if user_id.lower() in user["username"].lower():
                user_match = True  # NOSONAR
            elif ("email" in user) and user_id.lower() in user["email"].lower():
                user_match = True  # NOSONAR
            elif (
                ("attributes" in user) and "idir_username" in user["attributes"]
            ) and user_id.lower() in user["attributes"]["idir_username"][0].lower():
                user_match = True  # NOSONAR

            if user_match:
                matched_users.append(user)
        if user_and_email_only:
            matched_users = self.extractUsernameEmailFromuUserList(matched_users)
        LOGGER.debug(f"matched_users: {matched_users}")
        return matched_users

    def get_matching_users_with_role_mapping(self, user_id):
        """For a given string searches all the users and related roles and
        returns a data structure like:
        [ <username>, <email>, [<roles>...]]

        :param user_id: the input user_id
        :type user_id: str
        :return: list of users and the roles they belong to
        :rtype: list
        """
        users = self.get_matching_users(user_id, user_and_email_only=False)
        LOGGER.debug(f"users: {users}")
        role_mappings = []
        user_cnt = 0
        for user in users:
            print(f"user {user_cnt} of {len(users)}", end="\r", flush=True)
            # print('.', end='', flush=True) # noqa
            role_mapping = self.get_fom_user_role_mappings(user["id"])
            username_and_email = self.extractUsernameEmailFromuUser(user)
            username_and_email.append(role_mapping)
            LOGGER.debug(f"rolemaps: {role_mapping}")
            role_mappings.append(username_and_email)
            user_cnt += 1

        return role_mappings

    def extract_username_email_from_user_list(self, users):
        username_and_email_list = []
        for user in users:
            user_name_and_email = self.extractUsernameEmailFromuUser(user)
            username_and_email_list.append(user_name_and_email)
        return username_and_email_list

    def extract_username_email_from_user(self, user):
        LOGGER.debug(f"extract email from user : {user}")
        email = ""
        username = ""
        if "email" in user:
            email = user["email"]

        # if the user is an idir user the user object will have the following
        # properties:
        #     attributes:
        #         idir_user_guild list(str)
        #         idir_userid list(str)
        #         idir_username list(str)
        #         idir_username list(str)
        #         displayName list(str)
        # if (('attributes' in user) and
        #         'idir_username' in user['attributes']):
        username = user["username"]

        if not email and not user:
            msg = f"unable to extract email and username from this user: {user}"
            raise ValueError(msg)

        ret_val = [username, email]

        return ret_val

    def get_user_profile(self, user_id):
        # GET /{realm}/users/{id}

        url = f"{self.kc_realm_url}/users/{user_id}"  # noqa
        params = {"realm-name": constants.KC_HOST}
        response = requests.get(url=url, params=params, headers=self.default_headers)
        data = response.json()
        return data

    def get_fom_user_role_mappings(self, user_id, nameonly=True):
        """for a given user_id returns the rolemappings for that user id.  This
        is the user_id from keycloak, not the username.

        :param user_id: input user_id
        :type user_id: str
        :param nameonly: if set to true returns a list of only role names,
                         defaults to True
        :type nameonly: bool, optional
        :return: list of role mapping for the given user_id
        :rtype: list
        """
        fom_client = self.get_fom_client_id()
        LOGGER.debug(f"fom_client: {fom_client}")
        url = f"{self.kc_realm_url}/users/{user_id}/role-mappings/clients/{fom_client}"  # noqa
        LOGGER.debug(f"url: {url}")

        params = {"realm-name": constants.KC_HOST}
        LOGGER.debug(f"params: {params}")
        response = requests.get(url=url, params=params, headers=self.default_headers)
        data = response.json()
        return_data = data
        if nameonly:
            return_data = []
            for mapping in data:
                return_data.append(mapping["name"])
        return return_data

    def get_user_count(self):
        """returns the number of users that are currently configured in
        keycloak

        :return: the number of users in keycloak
        :rtype: int
        """
        url = f"{self.kc_realm_url}/users/count"  # noqa
        headers = self.default_headers
        params = {"realm-name": constants.KC_HOST}
        response = requests.get(url=url, params=params, headers=headers)
        data = response.json()
        return data

    def get_all_users(self):
        """Returns all the users currently configured in Keycloak

        :return: a list of objects from json describing all the users in
                 keycloak
        :rtype: list(dict)
        """

        # TODO: this is quick and dirty, could consider implementing a search
        #      in the api call for a specific user instead of returning all the
        #      users and then parsing that list

        user_cnt = self.get_user_count()
        LOGGER.debug(f"userCnt: {user_cnt}")

        page_size = 100
        first = 0

        user_data = []

        while len(user_data) < user_cnt:
            resp_data = self.get_user_page(first, page_size)
            user_data.extend(resp_data)
            LOGGER.debug(
                f"first: {first}, userdata cnt: {len(user_data)} "
                + f"usercount: {user_cnt}"
            )
            first = first + page_size

        LOGGER.debug(f"users returned: {len(user_data)}")
        return user_data

    def get_user_page(self, first, max):
        url = f"{self.kc_realm_url}/users"  # noqa
        params = {"realm-name": constants.KC_HOST, "max": max, "first": first}
        response = requests.get(url=url, params=params, headers=self.default_headers)
        resp_data = response.json()
        LOGGER.debug(f"status code: {response.status_code}")
        return resp_data

    def is_valid_user(self, user_id):
        """validates that the user provided exists in keycloak, and that the
        id is unique

        :param user_id: input user id to be validated
        :type user_id: str
        """
        is_valid = False
        users = self.get_all_users()
        LOGGER.debug(f"users: {users}")
        matches = []
        for user in users:
            if user["username"] == user_id:
                matches.append(user)
        if len(matches) == 1:
            is_valid = True
        return is_valid

    def get_roles(self, client_id):
        """returns a list of roles that exist within the provided client id"""
        roles_url = f"{self.kc_realm_url}/clients/{client_id}/roles"
        response = requests.get(url=roles_url, headers=self.default_headers)
        roles = response.json()
        LOGGER.debug(f"roles: {response.text}")

        return roles

    def get_role_users(self, client_id, role_name):
        # GET /{realm}/clients/{id}/roles/{role-name}/users
        role_user_url = (
            f"{self.kc_realm_url}/clients/{client_id}/roles/{role_name}/users"
        )
        response = requests.get(url=role_user_url, headers=self.default_headers)
        user_roles = response.json()
        LOGGER.debug(f"users: {response.text}")
        return user_roles

    def get_fom_client_id(self):
        """Looks up the FOM client 'id' using the 'clientid'

        the client 'id' is usually what is required to create / modify objects
        in / for / on behalf of the client
        """
        client_data = self.get_clients()
        fom_client = None
        for client in client_data:
            if client["clientId"] == constants.KC_FOM_CLIENTID:
                fom_client = client["id"]
        return fom_client

    def create_role(self, forest_client_id, description):
        """Creates the role for the forest client id if it doesn't already
        exist.

        * send payload/body where {"name":"role name to create"}
        * end point /auth/admin/realms/$REALM/clients/$CLIENTID/roles
        * method POST
        """
        # self.fcUtil.
        if not self.fom_role_exists(forest_client_id):
            role_name = self.fcUtil.get_role_name(forest_client_id)
            LOGGER.debug(f"rolename: {role_name}")

            clientid = self.get_fom_client_id()
            url = f"{self.kc_realm_url}/clients/{clientid}/roles"  # noqa
            data = {"name": role_name, "description": description}
            headers = self.default_headers
            headers["Content-type"] = APP_JSON
            headers["Accept"] = APP_JSON
            response = requests.post(url=url, headers=headers, json=data)
            response.raise_for_status()

    def remove_role(self, client_id, role_name):
        """_summary_

        :param client_id: _description_
        :type client_id: _type_
        :param role_name: _description_
        :type role_name: _type_

        https://$KC_URL/auth/admin/realms/$REALM/clients/{id}/roles/{role-name}

        """
        LOGGER.debug(f"client_id: {client_id}")
        LOGGER.debug(f"role_name: {role_name}")
        url = f"{self.kc_realm_url}/clients/{client_id}/roles/{role_name}"  # noqa
        headers = self.default_headers
        headers["Content-type"] = APP_JSON
        headers["Accept"] = APP_JSON
        LOGGER.debug(f"deleting the role: {role_name}")
        response = requests.delete(url=url, headers=headers)
        response.raise_for_status()
        LOGGER.debug(f"response: {response.status_code}")

    def get_clients(self):
        """
        GET /{realm}/clients
        """
        url = f"{self.kc_realm_url}/clients"  # noqa
        headers = self.default_headers
        headers["Content-type"] = APP_JSON
        headers["Accept"] = APP_JSON
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        LOGGER.debug(f"response: {response.status_code}")

        data = response.json()
        return data

    def get_client(self, client_id):
        """gets a list of all the clients in the realm and returns only the
        client that matches the client_id provided
        """
        clients = self.get_clients()
        client = None
        for client in clients:
            if client["clientId"].lower() == client_id.lower():
                break
        return client

    def add_role_to_user(self, user_id, forest_client_id):
        """This is the role mapping exercise...

        /auth/admin/realms/$REALM/users/$USERID/role-mappings/clients/$CLIENTID
        USERID - comes from user['id']

        assumes that the forestclientid and the user_id have been
        validated then does the role mapping

        https://$KC_URL/auth/admin/realms/$REALM/users/$user_id/role-mappings/clients/$fom_client_id

        1. get user id
        1. get client id
        1. get role
        """
        users = self.get_all_users()
        match_users = []
        for user in users:
            if user["username"] == user_id:
                match_users.append(user)

        # TODO: make sure only one user
        LOGGER.debug(f"users length {len(match_users)}")

        roles = self.get_fom_roles(forest_client_id)
        LOGGER.debug(f"roles length {len(roles)}")
        LOGGER.debug(f"role length {roles}")

        clientid = self.get_fom_client_id()

        url = f"{self.kc_realm_url}/users/{match_users[0]['id']}/role-mappings/clients/{clientid}"  # noqa
        headers = self.default_headers
        headers["Content-type"] = APP_JSON
        headers["Accept"] = APP_JSON

        response = requests.post(url=url, headers=headers, json=roles)
        response.raise_for_status()
