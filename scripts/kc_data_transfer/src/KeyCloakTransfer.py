import logging
import re
from typing import Union, List, TypedDict, Optional

import KeyCloak
import requests
import constants

# types

KCRole = TypedDict(
    "KCRole",
    {
        "id": str,
        "name": str,
        "description": str,
        "composite": bool,
        "clientRole": bool,
        "containerId": str,
    },
)

KCIdirAtributes = TypedDict(
    "KCIdirAtributes",
    {
        "idir_user_guid": List[str],
        "idir_userid": List[str],
        "idir_username": List[str],
        "displayName": List[str],
    },
)

KCUser = TypedDict(
    "KCUser",
    {
        "id": str,
        "createdTimestamp": str,
        "username": str,
        "enabled": bool,
        "totp": bool,
        "emailVerified": bool,
        "firstName": str,
        "lastName": str,
        "email": str,
        "requiredActions": List[Optional[Union[None, str]]],
        "disableableCredentialTypes": List[Optional[Union[str, None]]],
        "notBefore": int,
        "attributes": KCIdirAtributes,
        "idir_user_guid": List[str],
    },
)

FamApplication = TypedDict(
    "FamApplication",
    {
        "application_name": str,
        "application_description": str,
        "application_client_id": Union[int, None],
        "application_id": int,
        "create_user": Optional[Union[str, None]],
        "create_date": Optional[Union[str, None]],
        "update_user": Optional[Union[str, None]],
        "update_date": Optional[Union[str, None]],
    },
)

FamUser = TypedDict(
    "FamUser",
    {
        "role_name": str,
        "role_purpose": str,
        "parent_role_id": Union[str, None],
        "application_id": int,
        "forest_client_number": str,
        "create_user": str,
        "role_type_code": str,
        "client_number": Union[int, None],
        "update_user": str,
        "create_date": str,
        "update_date": str,
        "application": List[FamApplication],
    },
)

FamForestClient = TypedDict(
    "FamForestClient",
    {"forest_client_number": str, "create_user": Optional[Union[None, str]]},
)

FamRole = TypedDict(
    "FamRole",
    {
        "role_name": str,
        "role_purpose": str,
        "parent_role_id": Union[None, int],
        "application_id": int,
        "forest_client_number": Union[None, int],
        "create_user": Optional[Union[None, str]],
        "role_type_code": str,
        "client_number": Union[None, FamForestClient],
        "role_id": int,
        "update_user": Optional[Union[None, str]],
        "create_date": Optional[Union[None, str]],
        "update_date": Optional[Union[None, str]],
        "application": List[FamApplication],
    },
)


class KeyCloakToFAM:
    def __init__(self):
        self.kc = KeyCloak.KeycloakWrapper()
        # the name of the abstract role, and the prefix that will be
        # attached to related concrete roles
        # so for each concrete / forest client based role will create a
        # role that looks like:
        #   FOM_SUBMITTER_TESTING_00001011, FOM_SUBMITTER_TESTING_00001012... etc
        self.fom_submitter_parent_role_name = "FOM_SUBMITTER"
        self.fom_reviewer_role_name = "FOM_REVIEWER"
        self.fam = FamWrapper(
            fom_forest_client_role_parent=self.fom_submitter_parent_role_name
        )

    def copy_users(self):

        app_id = self.fam.get_fom_app_id()

        # Initialize the correct IDs for FOM_SUBMITTER and FOM_REVIEWER
        roles = self.fam.get_roles(app_id)
        for fam_role in roles:
            role_name = fam_role["role_name"]
            role_id = fam_role["role_id"]
            if role_name == self.fom_reviewer_role_name:
                self.fom_reviewer_role_id = role_id
            if role_name == self.fom_submitter_parent_role_name:
                self.fom_submitter_parent_role_id = role_id

        keycloak_roles = self.get_keycloak_roles()

        # iterate over each forest client based role from FOM in Keycloak
        for kc_role in keycloak_roles:

            kc_role_name = kc_role["name"]

            # These two roles are not used in FOM -- mistaken confign to ignore
            if kc_role_name in ['fom_forest_client_1011', 'fom_forest_client_1012']:
                continue

            # extract the fc 8 digit id / string from the role name
            forest_client_string = self.extract_forest_client(kc_role_name)

            fam_role_id = None
            if kc_role_name == 'fom_ministry':
                fam_role_id = self.fom_reviewer_role_id
            else:
                fam_role_id = self.fom_submitter_parent_role_id

            # get the keycloak users for the current forest client role
            users = self.kc.get_role_users(role_name=kc_role["name"])

            # iterate over each of the keycloak users and call the role assignment
            # end point to add them to FAM
            for user in users:
                user_type_code = self.get_user_type_code(user)

                # do the role assignment
                fam_user_name = self.extract_user_name(user, user_type_code)

                LOGGER.info(
                    f", {fam_role_id}, {forest_client_string}, {user_type_code}, {fam_user_name}"
                )
                self.fam.create_user_role_assignment(
                    user_type_code=user_type_code,
                    user_name=fam_user_name,
                    role_id=fam_role_id,
                    role_type_code="C",
                    forest_client_number=forest_client_string,
                )

    def extract_user_name(self, kc_user, user_type_code):
        """extracts the bceid user or the idir user from the user depending
        on the user type

        :param kc_user: _description_
        """
        LOGGER.debug(f"kc_user: {kc_user}")
        if user_type_code == "B":
            username = kc_user["username"]
        elif user_type_code == "I":
            username = kc_user["attributes"]["idir_username"][0].upper()
        return username

    def get_user_type_code(self, kc_user: KCUser) -> str:
        """gets a keycloak user struct, if has attributes
        attributes.idir_user_guid
        attributes.idir_userid
        attributes.idir_username

        then type is 'I'
        otherwise assume type is 'B'

        :param kc_user: _description_
        """
        return_type = "B"
        if "attributes" in kc_user:
            idir_attribs = ["idir_user_guid", "idir_userid", "idir_username"]
            if set(idir_attribs).issubset(set(kc_user["attributes"])):
                return_type = "I"
            else:
                return_type = "B"
        return return_type

    def extract_forest_client(self, role_name: str) -> Union[None, str]:
        """
        fom roles are stored like:
            fom_forest_client_00002176

        where the final _ portion is the forest client, this method parses
        that string and return the forest_client number

        :param role_name: _description_
        """
        int_regex = re.compile("[0-9]{8}")  # NOSONAR
        role_part_list = role_name.split("_")
        fc_candidate = role_part_list[-1]
        if int_regex.match(fc_candidate):
            return fc_candidate
        else:
            return None

    def extract_forest_client_roles(self, roles: List[KCRole]) -> List[KCRole]:
        """gets a list of key cloak roles, returns only roles
        that are fom / forest client roles

        :param roles: a list of role objects
        :return: a filtered list of role objects, returning only those that are
            forest client roles.
        """
        fom_fc_roles = []
        regex = re.compile("^fom_forest_client_[0-9]{8}$")  # NOSONAR
        for role in roles:
            LOGGER.debug(f"current role: {role}")
            if regex.match(role["name"]):
                fom_fc_roles.append(role)
            else:
                LOGGER.info(role["name"])
        return fom_fc_roles

    def get_fam_forest_client_role_name(self, forest_client_number: str) -> str:
        """calculates the name of the forest client number based role that will
        be used in FAM

        :param forest_client_number: the input forest client number
        :return: calculated forest client number based role.
        """
        role_name = f"{self.fom_submitter_parent_role_name}_{forest_client_number}"
        return role_name

    def get_keycloak_roles(self):
        # Retrieve the FOM client id from Keycloak
        client_id = self.kc.get_fom_client_id()
        LOGGER.debug(f"Keycloak client_id: {client_id}")

        # getting roles for the keycloak client
        roles = self.kc.get_roles(client_id=client_id)
        LOGGER.debug(f"number of keycloak roles: {len(roles)}")

        return roles


class FamWrapper:
    """The wrapper class for interactions with the FAM API"""

    def __init__(self, fom_forest_client_role_parent: str):
        """_summary_

        :param fom_forest_client_role_parent: abstract role that all subsequent
            forest client roles (concrete roles) will be related to.
        """
        # url to the FAM implementation
        self.url = constants.FAM_URL
        # default headers
        self.default_headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + constants.FAM_JWT
        }
        self.fom_forest_client_roles_parent = fom_forest_client_role_parent
        self.fom_forest_client_role_prefix = f"{fom_forest_client_role_parent}_"
        self.fom_app_id: Union[int, None] = None
        self.create_user_name = "KC_MIGRATION"

    def create_user_role_assignment(
        self,
        user_name: str,
        role_id: int,
        role_type_code: str,
        forest_client_number: str,
        user_type_code: str,
    ) -> None:
        """Creates a user / role assignment

        :param user_name: name of the user that is to be added
        :param role_id: The role id that the user should be added to
        :param role_type_code: The role type code (always C)
        :param forest_client_number: The forest client number for the new role
        :param user_type_code: The user type, ie B - BCEID, I - IDIR
        """
        payload = {
            "user_name": user_name,
            "role_id": role_id,
            "forest_client_number": forest_client_number,
            "role_type_code": role_type_code,
            "user_type_code": user_type_code,
        }
        url = f"{self.url}/user_role_assignment"
        resp = requests.post(url=url, headers=self.default_headers, json=payload)
        LOGGER.debug(f"status_code: {resp.status_code}")

    def get_roles(self, app_id) -> List[FamRole]:
        """Returns a list of objects the describe the fam_roles

        :return: list[dict]
        """
        url = f"{self.url}/fam_applications/{app_id}/fam_roles"
        resp = requests.get(url=url, headers=self.default_headers)
        LOGGER.debug(f"resp.text: {resp.text}")
        data = resp.json()
        return data

    def get_role(
        self, role_name: str, app_id: int
    ) -> Union[FamRole, None]:
        """retrieves all the fam role for an application, then iterates over the returned roles
        searching for a role that matches the input args

        :param role_name: The name of the role that should be returned
        :param role_type: The type of the role that should be returned
        :param app_id: If supplied the application id that the roles should
            be a part of
        :return: a role object that matches criteria above
        """
        return_role = None
        roles = self.get_roles(app_id)
        LOGGER.debug(f"role name to get: {role_name}")
        LOGGER.debug(f"role names: {[role['role_name'] for role in roles]}")
        for role in roles:
            if role["role_name"] == role_name:
                return_role = role
                break
        return return_role

    def get_apps(self) -> List[FamApplication]:
        url = f"{self.url}/fam_applications"
        resp = requests.get(url=url, headers=self.default_headers)
        LOGGER.debug(f"status_code: {resp.status_code}")
        LOGGER.debug(f"apps: {resp.text}")
        data = resp.json()
        return data

    def get_fom_app_id(self) -> Union[int, None]:

        app_id = None
        # app id isn't going to change so should only get it once, then cache
        # it in the property fom_app_id
        if self.fom_app_id is None:
            apps = self.get_apps()
            app_id = None
            for app in apps:
                if app["application_name"] == constants.FOM_APP_NAME_IN_FAM:
                    app_id = app["application_id"]
                    self.fom_app_id = app_id
                    break
        return app_id


if __name__ == "__main__":

    # simple logger setup
    LOGGER = logging.getLogger()
    LOGGER.setLevel(logging.INFO)
    hndlr = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s"
    )
    hndlr.setFormatter(formatter)
    LOGGER.addHandler(hndlr)
    LOGGER.debug("test")

    # transfer the users from Keycloak to FAM
    kc_2_fam = KeyCloakToFAM()
    kc_2_fam.copy_users()
