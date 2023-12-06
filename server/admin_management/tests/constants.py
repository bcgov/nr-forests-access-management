from api.app import constants as famConstants


TEST_CREATOR = "TESTER"
TEST_FOM_DEV_ADMIN_ROLE = "FOM_DEV_ACCESS_ADMIN"
INVALID_APPLICATION_ID = "invalid_application_id"

# ---------------------- test user data ----------------------------- #
TEST_INVALID_USER_TYPE = "NS"
TEST_NON_EXISTS_COGNITO_USER_ID = f"dev-idir_nonexists@idir"

TEST_NEW_USER = {
    "user_type_code": famConstants.UserType.IDIR,
    "user_name": "TEST_USER",
    "create_user": TEST_CREATOR,
}

# ---------------------- test application data ---------------------- #
TEST_NOT_EXIST_APPLICATION_ID = 0
TEST_APPLICATION_ID_FAM = 1
TEST_APPLICATION_NAME_FAM = "FAM"

# -------------------- test application admin data ------------------ #
TEST_APPLICATION_ADMIN_APPLICATION_ID = 3
TEST_NEW_APPLICATION_ADMIN_USER_ID = 1
TEST_NEW_APPLICATION_ADMIN = {
    "user_type_code": famConstants.UserType.BCEID,
    "user_name": "TEST_USER",
    "application_id": TEST_APPLICATION_ADMIN_APPLICATION_ID,
}
