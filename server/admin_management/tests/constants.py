import os

from api.app import constants as famConstants
import api.app.schemas as schemas
from api.app.services.role_service import RoleService


TEST_CREATOR = "TESTER"
TEST_ANOTHER_CREATER = "TESTERTWO"
TEST_FOM_DEV_ADMIN_ROLE = "FOM_DEV_ADMIN"
TEST_FAM_ADMIN_ROLE = "FAM_ADMIN"
INVALID_APPLICATION_ID = "invalid_application_id"
TEST_APP_FOM_NAME = "FOM"
TEST_APP_ROLE_NAME_FOM_REVIEWER = "FOM_REVIEWER"
TEST_APP_ROLE_NAME_FOM_SUBMITTER = "FOM_SUBMITTER"

# ---------------------- test user data ----------------------------- #
TEST_NON_EXIST_USER_ID = 0
TEST_USER_ID = 1
TEST_INVALID_USER_TYPE = "NS"
TEST_NON_EXISTS_COGNITO_USER_ID = f"dev-idir_nonexists@idir"
TEST_DUMMY_COGNITO_USER_ID = f"dev-idir_dummyid@idir"
TEST_USER_NAME = "TEST_USER"

TEST_NEW_IDIR_USER = schemas.FamUserDto(
    **{
        "user_type_code": famConstants.UserType.IDIR,
        "user_name": TEST_USER_NAME,
        "create_user": TEST_CREATOR,
    }
)

TEST_NEW_BCEID_USER = schemas.FamUserDto(
    **{
        "user_type_code": famConstants.UserType.BCEID,
        "user_name": TEST_USER_NAME,
        "create_user": TEST_CREATOR,
    }
)

TEST_USER_GUID_IDIR = ""  # once we implement the user validation in backend, this might need change to a real guid

# ---------------------- test application data ---------------------- #
TEST_NOT_EXIST_APPLICATION_ID = 0
TEST_APPLICATION_ID_FAM = 1
TEST_APPLICATION_ID_FOM_DEV = 2
TEST_APPLICATION_ID_FOM_TEST = 3
TEST_APPLICATION_NAME_FAM = "FAM"

# -------------------- test application admin data ------------------ #
TEST_APPLICATION_ADMIN_APPLICATION_ID = 3
TEST_NEW_APPLICATION_ADMIN_USER_ID = 1
TEST_NEW_APPLICATION_ADMIN = {
    "user_type_code": famConstants.UserType.IDIR,
    "user_name": TEST_USER_NAME,
    "user_guid": TEST_USER_GUID_IDIR,
    "application_id": TEST_APPLICATION_ADMIN_APPLICATION_ID,
}

# -------------------- test forest client data ---------------------- #
TEST_NON_EXIST_FOREST_CLIENT_NUMBER = "99999999"
TEST_INVALID_FOREST_CLIENT_NUMBER = "12345"
TEST_INACTIVE_FOREST_CLIENT_NUMBER = "00000002"
TEST_FOREST_CLIENT_NUMBER = "00001011"
TEST_FOREST_CLIENT_NUMBER_TWO = "00000001"
TEST_FOERST_CLIENT_CREATE = schemas.FamForestClientCreateDto(
    **{
        "forest_client_number": TEST_FOREST_CLIENT_NUMBER,
        "create_user": TEST_CREATOR,
    }
)

# -------------------------- test role data ------------------------- #
TEST_NOT_EXIST_ROLE_ID = 0
TEST_FOM_DEV_SUBMITTER_ROLE_ID = 3
TEST_FOM_DEV_REVIEWER_ROLE_ID = 4
TEST_FOM_TEST_SUBMITTER_ROLE_ID = 7
TEST_FOM_TEST_REVIEWER_ROLE_ID = 8
TEST_NON_EXIST_ROLE_NAME = "TEST_NON_EXIST_ROLE"
TEST_FOM_SUBMITTER_ROLE_NAME = "FOM_SUBMITTER"
TEST_FOM_REVIEWER_ROLE_NAME = "FOM_REVIEWER"

TEST_NEW_ROLE = "TEST_READ"
TEST_NEW_ROLE_TWO = "TEST_WRITE"
TEST_ROLE_PURPOSE = "test role"
TEST_ROLE_CREATE_CONCRETE = {
    "application_id": TEST_APPLICATION_ID_FOM_DEV,
    "role_name": TEST_NEW_ROLE,
    "role_purpose": TEST_ROLE_PURPOSE,
    "create_user": TEST_CREATOR,
    "role_type_code": famConstants.RoleType.ROLE_TYPE_CONCRETE,
}  # this is used for repository level test
TEST_ROLE_CREATE_ABSTRACT = {
    **TEST_ROLE_CREATE_CONCRETE,
    "role_name": TEST_NEW_ROLE_TWO,
    "role_type_code": famConstants.RoleType.ROLE_TYPE_ABSTRACT,
}  # this is used for repository level test
TEST_ROLE_CREATE_CHILD = schemas.FamRoleCreateDto(
    **{
        "parent_role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
        "application_id": TEST_APPLICATION_ID_FOM_DEV,
        "forest_client_number": TEST_FOREST_CLIENT_NUMBER,
        "role_name": RoleService.construct_forest_client_role_name(
            TEST_FOM_SUBMITTER_ROLE_NAME, TEST_FOREST_CLIENT_NUMBER
        ),
        "role_purpose": RoleService.construct_forest_client_role_purpose(
            "PARENT_ROLE purpose", TEST_FOREST_CLIENT_NUMBER
        ),
        "create_user": TEST_CREATOR,
        "role_type_code": famConstants.RoleType.ROLE_TYPE_CONCRETE,
    }
)  # this is an object variable because we use it in both service and repository test

# -------------------- test access control privilege data ------------------ #
TEST_NON_EXIST_ACCESS_CONTROL_PRIVILEGE_ID = 0
TEST_ACCESS_CONTROL_PRIVILEGE_CREATE = schemas.FamAccessControlPrivilegeCreateDto(
    **{
        "user_id": TEST_USER_ID,
        "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
        "create_user": TEST_CREATOR,
    }
)
TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST = {
    "user_name": TEST_USER_NAME,
    "user_guid": TEST_USER_GUID_IDIR,
    "user_type_code": famConstants.UserType.IDIR,
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_numbers": [TEST_FOREST_CLIENT_NUMBER],
}

TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST_CONCRETE = {
    "user_name": TEST_USER_NAME,
    "user_guid": TEST_USER_GUID_IDIR,
    "user_type_code": famConstants.UserType.IDIR,
    "role_id": TEST_FOM_DEV_REVIEWER_ROLE_ID,
}

# -------------------------- error messages ------------------------- #
ERROR_VOLIATE_UNIQUE_CONSTRAINT = "duplicate key value violates unique constraint"
ERROR_VOLIATE_FOREIGN_KEY_CONSTRAINT = "violates foreign key constraint"
