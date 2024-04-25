import os
from api.app import constants as fam_constants


FOM_DEV_APPLICATION_ID = 2
FOM_TEST_APPLICATION_ID = 3
NOT_EXIST_APPLICATION_ID = 0

FOM_DEV_SUBMITTER_ROLE_ID = 3
FOM_DEV_REVIEWER_ROLE_ID = 4
FOM_TEST_SUBMITTER_ROLE_ID = 7
FOM_TEST_REVIEWER_ROLE_ID = 8
NOT_EXIST_ROLE_ID = 0

ROLE_NAME_FOM_REVIEWER = "FOM_REVIEWER"
ROLE_NAME_FOM_SUBMITTER_00001018 = "FOM_SUBMITTER_00001018"
ROLE_NAME_FOM_SUBMITTER_00000001 = "FOM_SUBMITTER_00000001"

TEST_CREATOR = "TESTER"
TEST_USER_ID = 1
USER_NAME_BCEID_LOAD_3_TEST = "LOAD-3-TEST"
USER_NAME_BCEID_LOAD_4_TEST = "LOAD-4-TEST"

# Testing Forest Client numbers
FC_NUMBER_LEN_TOO_SHORT = "0001011"
FC_NUMBER_LEN_TOO_LONG = "000001011"
FC_NUMBER_NOT_EXISTS = "99999999"
"""
Forest Client API has following status codes.
    ACT (Active) - client "00000001"
    DAC (Deactivated) - client "00000002"
    DEC (Deceased) - client "00152880"
    REC (Receivership) - client "00169575"
    SPN (Suspended) - client "00003643"
"""
FC_NUMBER_EXISTS_ACTIVE_00000001 = "00000001"
FC_NUMBER_EXISTS_ACTIVE_00001011 = "00001011"
FC_NUMBER_EXISTS_ACTIVE_00001018 = "00001018"
FC_NUMBER_EXISTS_DEACTIVATED = "00000002"
FC_NUMBER_EXISTS_DECEASED = "00152880"
FC_NUMBER_EXISTS_RECEIVERSHIP = "00169575"
FC_NUMBER_EXISTS_SUSPENDED = "00003643"


TEST_NEW_USER = {
    "user_type_code": "I",
    "user_name": "TEST_USER",
    "create_user": TEST_CREATOR,
}
TEST_NOT_EXIST_USER_TYPE = "NS"

# Admin role level at token
FOM_DEV_ADMIN_ROLE = "FOM_DEV_ADMIN"
FOM_TEST_ADMIN_ROLE = "FOM_TEST_ADMIN"

# ------------------- Test grant/remove access -------------------------- #
# Note:
# The test idir and bceid username might need change to a real one after we
#   enable the verfication, same for forest client number.
#
# Please refer to flyway/local_sql/V1001__add_delegated_admin_for_testing
#   script for pre-test admin testers setup (needed for tests)".
#   "TEST-3-LOAD-CHILD-1" and "PTOLLEST" are being setup as delegated admin.
#
# Note:
# Do not change bellow various configuration for user role assignments (ACCESS_
#   GRANT) unless needed (refactoring is required if it is changed).
# If there is a need for additional configuration, perhaps, better to "copy"
#   on of them and assign individual values in specific test cases.
#
# Note: (variable uses these to shorter the name)
#   _AR_ : Abstract Role
#   _CR_ : Concrete Role
#   _L3T_: LOAD_3_TEST
#   _L4T_: LOAD_4_TEST

ACCESS_GRANT_FOM_DEV_CR_IDIR = {
    "user_name": "fom_user_test",
    "user_type_code": fam_constants.UserType.IDIR,
    "role_id": FOM_DEV_REVIEWER_ROLE_ID,
}

ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR = {
    "user_name": "fom_user_test",
    "user_type_code": fam_constants.UserType.IDIR,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": FC_NUMBER_EXISTS_ACTIVE_00000001,
}

ACCESS_GRANT_FOM_DEV_AR_00001018_IDIR = {
    "user_name": "fom_user_test",
    "user_type_code": fam_constants.UserType.IDIR,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": FC_NUMBER_EXISTS_ACTIVE_00001018,
}

ACCESS_GRANT_FOM_TEST_CR_IDIR = {
    "user_name": "fom_user_test",
    "user_type_code": "I",
    "role_id": FOM_TEST_REVIEWER_ROLE_ID,
}

ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T = {
    "user_name": USER_NAME_BCEID_LOAD_3_TEST,
    "user_type_code": "B",
    "role_id": FOM_DEV_REVIEWER_ROLE_ID,
}

ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T = {
    "user_name": USER_NAME_BCEID_LOAD_4_TEST,
    "user_type_code": "B",
    "role_id": FOM_DEV_REVIEWER_ROLE_ID,
}

ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID = {
    "user_name": "fom_user_test",
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": FC_NUMBER_EXISTS_ACTIVE_00000001,
}

ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID_L3T = {
    "user_name": USER_NAME_BCEID_LOAD_3_TEST,
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": FC_NUMBER_EXISTS_ACTIVE_00000001,
}

ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T = {
    "user_name": USER_NAME_BCEID_LOAD_3_TEST,
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": FC_NUMBER_EXISTS_ACTIVE_00001018,
}

ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L4T = {
    "user_name": USER_NAME_BCEID_LOAD_4_TEST,
    "user_type_code": "B",
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": FC_NUMBER_EXISTS_ACTIVE_00001018,
}

ACCESS_GRANT_FOM_TEST_AR_00001018_BCEID_L4T = {
    "user_name": USER_NAME_BCEID_LOAD_4_TEST,
    "user_type_code": "B",
    "role_id": FOM_TEST_SUBMITTER_ROLE_ID,
    "forest_client_number": FC_NUMBER_EXISTS_ACTIVE_00001018,
}

# -------- Test IDIM Proxy API for searching IDIR and BCEID ---------- #
TEST_IDIR_REQUESTER_DICT = {
    "cognito_user_id": "test-idir_e72a12c916a44f39e5dcdffae7@idir",
    "user_name": "IANLIU",
    "user_type_code": fam_constants.UserType.IDIR,
    "user_id": 4,
    "user_guid": os.environ.get("TEST_IDIR_USER_GUID"),
}
TEST_BCEID_REQUESTER_DICT = {
    "cognito_user_id": "test-bceidbusiness_532905de0aa24923ae535428f171bf13@bceidbusiness",
    "user_name": "LOAD-3-TEST",
    "user_type_code": "B",
    "user_id": 10,  # this is a fake user id, it doesn't matter
    "user_guid": "532905DE0AA24923AE535428F171BF13",
    "business_guid": "E7C0431DA55D4ACA9FA901EE2C91CB3B",
}
TEST_VALID_BUSINESS_BCEID_USERNAME_ONE = "TEST-3-LOAD-CHILD-1"
TEST_VALID_BUSINESS_BCEID_USERNAME_TWO = "LOAD-2-TEST"
