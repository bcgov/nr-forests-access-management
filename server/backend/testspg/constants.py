import os
from api.app import constants as fam_constants


TEST_FOM_DEV_APPLICATION_ID = 2
TEST_FOM_TEST_APPLICATION_ID = 3
TEST_NOT_EXIST_APPLICATION_ID = 0

TEST_FOM_DEV_SUBMITTER_ROLE_ID = 3
TEST_FOM_DEV_REVIEWER_ROLE_ID = 4
TEST_FOM_TEST_REVIEWER_ROLE_ID = 8
TEST_NOT_EXIST_ROLE_ID = 0

TEST_CREATOR = "TESTER"
TEST_USER_ID = 1

# Testing Forest Client numbers (TEST Environment)
CLIENT_NUMBER_LEN_TOO_SHORT = "0001011"
CLIENT_NUMBER_LEN_TOO_LONG = "000001011"
CLIENT_NUMBER_NOT_EXISTS = "99999999"
"""
Forest Client API has following status codes.
    ACT (Active) - client "00000001"
    DAC (Deactivated) - client "00000002"
    DEC (Deceased) - client "00152880"
    REC (Receivership) - client "00169575"
    SPN (Suspended) - client "00003643"
"""
CLIENT_NUMBER_EXISTS_ACTIVE = "00000001"
CLIENT_NUMBER_EXISTS_ACTIVE_00001011 = "00001011"
CLIENT_NUMBER_EXISTS_ACTIVE_00001018 = "00001018"
CLIENT_NUMBER_EXISTS_DEACTIVATED = "00000002"
CLIENT_NUMBER_EXISTS_DECEASED = "00152880"
CLIENT_NUMBER_EXISTS_RECEIVERSHIP = "00169575"
CLIENT_NUMBER_EXISTS_SUSPENDED = "00003643"

# ------------------- Test user ------------------------------------ #

TEST_NEW_USER = {
    "user_type_code": "I",
    "user_name": "TEST_USER",
    "create_user": TEST_CREATOR,
}
TEST_NOT_EXIST_USER_TYPE = "NS"

USER_GUID_IDIR = os.environ.get("USER_GUID_IDIR") or ""
USER_GUID_BCEID_LOAD_3_TEST = "532905DE0AA24923AE535428F171BF13"


# ------------------- Test grant/remove access -------------------------- #
# note:
# test idir and bceid username might need change to a
# real one after we enable the verfication, same for
# forest client number
TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE = {
    "user_name": "fom_user_test",
    "user_guid": USER_GUID_IDIR,
    "user_type_code": "I",
    "role_id": TEST_FOM_DEV_REVIEWER_ROLE_ID,
}
TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT = {
    "user_name": "fom_user_test",
    "user_guid": USER_GUID_IDIR,
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": CLIENT_NUMBER_EXISTS_ACTIVE,
}
TEST_USER_ROLE_ASSIGNMENT_FOM_TEST_CONCRETE = {
    "user_name": "fom_user_test",
    "user_guid": USER_GUID_IDIR,
    "user_type_code": "I",
    "role_id": TEST_FOM_TEST_REVIEWER_ROLE_ID,
}

TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE_BCEID = {
    "user_name": "LOAD-3-TEST",
    "user_guid": USER_GUID_BCEID_LOAD_3_TEST,
    "user_type_code": "B",
    "role_id": TEST_FOM_DEV_REVIEWER_ROLE_ID,
}
TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT_BCEID = {
    "user_name": "LOAD-3-TEST",
    "user_guid": USER_GUID_BCEID_LOAD_3_TEST,
    "user_type_code": "B",
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": CLIENT_NUMBER_EXISTS_ACTIVE_00001018,  # note this is matched with the test delegated admin privilege in local sql
}


# -------- Test IDIM Proxy API for searching IDIR and BCEID ---------- #
TEST_IDIR_REQUESTER_DICT = {
    "cognito_user_id": "test-idir_e72a12c916a44f39e5dcdffae7@idir",
    "user_name": "IANLIU",
    "user_type_code": fam_constants.UserType.IDIR,
    "user_id": 4,
    "user_guid": USER_GUID_IDIR,
}
TEST_BCEID_REQUESTER_DICT = {
    "cognito_user_id": "test-bceidbusiness_532905de0aa24923ae535428f171bf13@bceidbusiness",
    "user_name": "LOAD-3-TEST",
    "user_type_code": fam_constants.UserType.BCEID,
    "user_id": 10,  # this is a fake user id, it doesn't matter
    "user_guid": USER_GUID_BCEID_LOAD_3_TEST,
    "business_guid": "E7C0431DA55D4ACA9FA901EE2C91CB3B",
}
TEST_VALID_BUSINESS_BCEID_USERNAME_ONE = "TEST-3-LOAD-CHILD-1"
TEST_VALID_BUSINESS_BCEID_USERNAME_TWO = "LOAD-2-TEST"
