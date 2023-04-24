
from api.app import constants as fam_constants

TEST_FOM_DEV_APPLICATION_ID = 2
TEST_FOM_TEST_APPLICATION_ID = 3

TEST_FOM_DEV_SUBMITTER_ROLE_ID = 3
TEST_FOM_DEV_REVIEWER_ROLE_ID = 4

TEST_FOM_TEST_REVIEWER_ROLE_ID = 8

TEST_NOT_EXIST_ROLE_ID = 0
TEST_NOT_EXIST_APPLICATION_ID = 0

TEST_CREATOR = "TESTER"

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
CLIENT_NUMBER_2_EXISTS_ACTIVE = "00001011"
CLIENT_NUMBER_EXISTS_DEACTIVATED = "00000002"
CLIENT_NUMBER_EXISTS_DECEASED = "00152880"
CLIENT_NUMBER_EXISTS_RECEIVERSHIP = "00169575"
CLIENT_NUMBER_EXISTS_SUSPENDED = "00003643"

# note:
# test idir and bceid username might need change to a
# real one after we enable the verfication, same for
# forest client number

TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE = {
    "user_name": "fom_user_test",
    "user_type_code": "I",
    "role_id": TEST_FOM_DEV_REVIEWER_ROLE_ID
}
TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT = {
    "user_name": "fom_user_test",
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": CLIENT_NUMBER_EXISTS_ACTIVE
}
TEST_USER_ROLE_ASSIGNMENT_FOM_TEST_CONCRETE = {
    "user_name": "fom_user_test",
    "user_type_code": "I",
    "role_id": TEST_FOM_TEST_REVIEWER_ROLE_ID
}

TEST_NEW_USER = {
    "user_type_code": "I",
    "user_name": "TEST_USER",
    "create_user": TEST_CREATOR,
}
TEST_NOT_EXIST_USER_TYPE = 'NS'
