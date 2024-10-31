from api.app import constants as fam_constants

# --------------------- Testing application  ---------------------------- #
FAM_APPLICATION_ID = 1
FOM_DEV_APPLICATION_ID = 2
FOM_TEST_APPLICATION_ID = 3
NOT_EXIST_APPLICATION_ID = 0


# --------------------- Testing role ----------------------------------- #
FOM_DEV_SUBMITTER_ROLE_ID = 3
FOM_DEV_REVIEWER_ROLE_ID = 4
FOM_TEST_SUBMITTER_ROLE_ID = 7
FOM_TEST_REVIEWER_ROLE_ID = 8
NOT_EXIST_ROLE_ID = 0

ROLE_NAME_FOM_REVIEWER = "FOM_REVIEWER"
ROLE_NAME_FOM_SUBMITTER_00001018 = "FOM_SUBMITTER_00001018"
ROLE_NAME_FOM_SUBMITTER_00000001 = "FOM_SUBMITTER_00000001"
NOT_EXIST_ROLE_NAME = "OTHER_APP_ROLE"


# ------------------- Testing user ------------------------------------ #

TEST_CREATOR = "TESTER"
TEST_USER_ID = 1
NOT_EXIST_TEST_USER_ID = 99999
TEST_USER_NAME_IDIR = "TEST_USER"
TEST_USER_GUID_IDIR = "MOCKEDGUID5D4ACA9FA901EE2C91CB3B"  # this is a faked user guid
TEST_USER_FIREST_NAME = "FIRST NAME"
TEST_USER_LAST_NAME = "LAST NAME"
TEST_USER_EMAIL = "EMAIL"
TEST_REQUESTER = {
    "cognito_user_id": "test-idir_e72a12c916afakedffae7@idir",
    "user_name": TEST_USER_NAME_IDIR,
    "user_guid":  TEST_USER_GUID_IDIR,
    "user_id": TEST_USER_ID,
    "first_name": TEST_USER_FIREST_NAME,
    "last_name": TEST_USER_LAST_NAME,
    "email": TEST_USER_EMAIL,
}

TEST_NOT_EXIST_USER_TYPE = "NS"

USER_NAME_BCEID_LOAD_2_TEST = "LOAD-2-TEST"
USER_GUID_BCEID_LOAD_2_TEST = "81069F39B35B4861BCD010582B63B112"
BUSINESS_GUID_BCEID_LOAD_2_TEST = (
    "MOCKEDBUSINESSGUID5D4ACA9FA901EE"  # this is a faked business guid
)
USER_NAME_BCEID_LOAD_3_TEST = "LOAD-3-TEST"
USER_GUID_BCEID_LOAD_3_TEST = "532905DE0AA24923AE535428F171BF13"
BUSINESS_GUID_BCEID_LOAD_3_TEST = "E7C0431DA55D4ACA9FA901EE2C91CB3B"
USER_NAME_BCEID_LOAD_3_TEST_CHILD_1 = "TEST-3-LOAD-CHILD-1"
USER_GUID_BCEID_LOAD_3_TEST_CHILD_1 = "BDA2A1E212244DC2B9F9522057C58BBB"
USER_NAME_BCEID_LOAD_4_TEST = "LOAD-4-TEST"
USER_GUID_BCEID_LOAD_4_TEST = "B1323E832A4A4947B50367EF4A4F79DE"
BUSINESS_GUID_BCEID_LOAD_4_TEST = "B1323E832A4A4947B50367EF4A4F79DE"


TEST_NEW_USER = {
    "user_type_code": fam_constants.UserType.IDIR,
    "user_name": TEST_USER_NAME_IDIR,
    "user_guid": TEST_USER_GUID_IDIR,
    "create_user": TEST_CREATOR,
}

TEST_NEW_BCEID_USER = {
    "user_type_code": fam_constants.UserType.BCEID,
    "user_name": USER_NAME_BCEID_LOAD_2_TEST,
    "user_guid": USER_GUID_BCEID_LOAD_2_TEST,
    "create_user": TEST_CREATOR,
}

TEST_USER_NAME_PREFIX = "TEST_USER_"
TEST_USER_NAME_IDIR_PREFIX = f"{TEST_USER_NAME_PREFIX}IDIR_"
TEST_USER_NAME_BCEID_PREFIX = f"{TEST_USER_NAME_PREFIX}BCEID_"
TEST_USER_EMAIL_SUFFIX = "fam.test.com"

# --------------------- Testing forest client numbers ----------------- #
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

MOCK_FIND_CLIENT_00001011_RETURN = [{
	'clientNumber': '00001011', 'clientName': 'AKIECA EXPLORERS LTD.', 'clientStatusCode': 'ACT', 'clientTypeCode': 'C'
}]

# --------------------- Testing Admin role level at token -------------- #
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
    "user_guid": TEST_USER_GUID_IDIR,
    "user_type_code": fam_constants.UserType.IDIR,
    "role_id": FOM_DEV_REVIEWER_ROLE_ID,
}

ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR = {
    "user_name": "fom_user_test",
    "user_guid": TEST_USER_GUID_IDIR,
    "user_type_code": fam_constants.UserType.IDIR,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_numbers": [FC_NUMBER_EXISTS_ACTIVE_00000001],
}

ACCESS_GRANT_FOM_DEV_AR_00001018_IDIR = {
    "user_name": "fom_user_test",
    "user_guid": TEST_USER_GUID_IDIR,
    "user_type_code": fam_constants.UserType.IDIR,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_numbers": [FC_NUMBER_EXISTS_ACTIVE_00001018],
}

ACCESS_GRANT_FOM_TEST_CR_IDIR = {
    "user_name": "fom_user_test",
    "user_guid": TEST_USER_GUID_IDIR,
    "user_type_code": fam_constants.UserType.IDIR,
    "role_id": FOM_TEST_REVIEWER_ROLE_ID,
}

ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T = {
    "user_name": USER_NAME_BCEID_LOAD_3_TEST,
    "user_guid": USER_GUID_BCEID_LOAD_3_TEST,
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": FOM_DEV_REVIEWER_ROLE_ID,
}

ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T = {
    "user_name": USER_NAME_BCEID_LOAD_4_TEST,
    "user_guid": USER_GUID_BCEID_LOAD_4_TEST,
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": FOM_DEV_REVIEWER_ROLE_ID,
}

ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID = {
    "user_name": USER_NAME_BCEID_LOAD_3_TEST,
    "user_guid": USER_GUID_BCEID_LOAD_3_TEST,
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_numbers": [FC_NUMBER_EXISTS_ACTIVE_00000001],
}

ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID_L3T = {
    "user_name": USER_NAME_BCEID_LOAD_3_TEST,
    "user_guid": USER_GUID_BCEID_LOAD_3_TEST,
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_numbers": [FC_NUMBER_EXISTS_ACTIVE_00000001],
}

ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T = {
    "user_name": USER_NAME_BCEID_LOAD_3_TEST,
    "user_guid": USER_GUID_BCEID_LOAD_3_TEST,
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_numbers": [FC_NUMBER_EXISTS_ACTIVE_00001018],
}

ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L4T = {
    "user_name": USER_NAME_BCEID_LOAD_4_TEST,
    "user_guid": USER_GUID_BCEID_LOAD_4_TEST,
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_numbers": [FC_NUMBER_EXISTS_ACTIVE_00001018],
}


# -------- Test IDIM Proxy API for searching IDIR and BCEID ---------- #
TEST_IDIR_REQUESTER_DICT = {
    "cognito_user_id": "test-idir_e72a12c916a44f39e5dcdffae7@idir",
    "user_name": "IANLIU",
    "user_type_code": fam_constants.UserType.IDIR,
    "user_id": 4,
    "user_guid": TEST_USER_GUID_IDIR,
}
TEST_BCEID_REQUESTER_DICT = {
    "cognito_user_id": f"test-bceidbusiness_{USER_GUID_BCEID_LOAD_3_TEST}@bceidbusiness",
    "user_name": USER_NAME_BCEID_LOAD_3_TEST,
    "user_type_code": fam_constants.UserType.BCEID,
    "user_id": 10,  # this is a fake user id, it doesn't matter
    "user_guid": USER_GUID_BCEID_LOAD_3_TEST,
    "business_guid": BUSINESS_GUID_BCEID_LOAD_3_TEST,
}
TEST_VALID_BUSINESS_BCEID_USERNAME_ONE = "TEST-3-LOAD-CHILD-1"
TEST_VALID_BUSINESS_BCEID_USERNAME_TWO = "LOAD-2-TEST"
