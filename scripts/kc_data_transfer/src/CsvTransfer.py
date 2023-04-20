import csv
import logging
from KeyCloakTransfer import FamWrapper
import constants

LOGGER = logging.getLogger(__name__)


class AppToFam:
    def __init__(self):
        self.path = constants.APP_USER_FILE_PATH
        self.fam = FamWrapper()

    def get_forest_client(self, organization: str):
        # get the forest client number from the "For Organization" column
        # if has one, it should be in the format of
        # "[forest_client_number] - [organization_name]"
        forest_client_num = organization.split('-')[0].replace(" ", "")
        if forest_client_num.isdigit():
            return forest_client_num
        return None

    def get_username_and_type(self, user: str):
        # get username and type from the "User" column in the csv file
        # it should be in the format of "USERSTYPE\USERNAME"
        user_info = user.split('\\')
        if len(user_info) == 2:
            if "IDIR" in user_info[0]:
                return "I", user_info[1]
            if "BCEID" in user_info[0]:
                return "B", user_info[1]

        return None, None

    def transfer_user_to_fam(self):
        app_id = self.fam.get_fom_app_id()
        users = self.read_file_data(self.path)

        for index, user in enumerate(users):
            user_type_code, username = self.get_username_and_type(user['User'])
            if user_type_code and username:
                role_name = user["Profile"]
                role_id = self.fam.get_role_id(role_name, app_id)

                if role_id:
                    print(index, username, user_type_code, role_id,
                          self.get_forest_client(user["For Organization"]))
                    self.fam.create_user_role_assignment(
                        user_type_code=user_type_code,
                        user_name=username,
                        role_id=role_id,
                        role_type_code="C",
                        forest_client_number=self.get_forest_client(
                            user["For Organization"]
                        ),
                    )
                else:
                    LOGGER.error("failed to find role, " +
                                 f"please check the data format: {user}")
            else:
                LOGGER.error("failed to get user name and user type, " +
                             f"please check the data format: {user}")

    def read_file_data(self, path: str):
        data = []
        column_title = []

        with open(path, newline='', encoding='utf-8-sig') as csvfile:
            file_content = csv.reader(csvfile, delimiter=',')
            for row in file_content:
                for col in row:
                    column_title.append(col)
                break

            for row in file_content:
                format_row = {}
                for index, col in enumerate(row):
                    format_row[column_title[index]] = col
                data.append(format_row)

        return data


if __name__ == "__main__":

    app = AppToFam()
    app.transfer_user_to_fam()
