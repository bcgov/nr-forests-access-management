
from api.app import constants as fam_constants

# TODO: Need to merge and refactor from current postgres tests PR #535

TEST_FOM_DEV_SUBMITTER_ROLE_ID = 3

TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT = {
    "user_name": "fom_user_test",
    "user_type_code": fam_constants.UserType.BCEID,
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": "10000000"
}


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
CLIENT_NUMBER_EXISTS_DEACTIVATED = "00000002"
CLIENT_NUMBER_EXISTS_DECEASED = "00152880"
CLIENT_NUMBER_EXISTS_RECEIVERSHIP = "00169575"
CLIENT_NUMBER_EXISTS_SUSPENDED = "00003643"
