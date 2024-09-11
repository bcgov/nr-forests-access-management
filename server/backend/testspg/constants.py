import datetime
from api.app import constants as fam_constants
from api.app.models.model import FamPrivilegeChangeAudit
from api.app.schemas.permission_audit_history import PermissionAuditHistoryResDto


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


# ------------------- Testing user ------------------------------------ #

TEST_CREATOR = "TESTER"
TEST_USER_ID = 1
TEST_USER_NAME_IDIR = "TEST_USER"
TEST_USER_GUID_IDIR = "MOCKEDGUID5D4ACA9FA901EE2C91CB3B"  # this is a faked user guid

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


# -------- Test constants for crud_permission_audit -------- #

USER_ID_1 = 1
USER_ID_2 = 2
APPLICATION_ID_1 = 1
APPLICATION_ID_2 = 2
CHANGE_DATE_1 = datetime(2024, 9, 10, 12, 0)
CHANGE_DATE_2 = datetime(2024, 9, 11, 12, 0)
PERFORMER_DETAILS_1 = {"username": "user1", "role": "admin"}
PERFORMER_DETAILS_2 = {"username": "user2", "role": "admin"}
PRIVILEGE_DETAILS = {"role": "submitter"}

AUDIT_RECORD_1 = FamPrivilegeChangeAudit(
    change_date=CHANGE_DATE_1,
    change_performer_user_details=PERFORMER_DETAILS_1,
    change_performer_user_id=USER_ID_1,
    change_target_user_id=USER_ID_1,
    create_date=CHANGE_DATE_1,
    create_user="admin",
    privilege_change_type_code="ADD",
    privilege_details=PRIVILEGE_DETAILS,
    application_id=APPLICATION_ID_1,
)

AUDIT_RECORD_2 = FamPrivilegeChangeAudit(
    change_date=CHANGE_DATE_2,
    change_performer_user_details=PERFORMER_DETAILS_2,
    change_performer_user_id=USER_ID_2,
    change_target_user_id=USER_ID_2,
    create_date=CHANGE_DATE_2,
    create_user="admin",
    privilege_change_type_code="REMOVE",
    privilege_details=PRIVILEGE_DETAILS,
    application_id=APPLICATION_ID_1,
)

AUDIT_RECORD_3 = FamPrivilegeChangeAudit(
    change_date=CHANGE_DATE_2,
    change_performer_user_details=PERFORMER_DETAILS_1,
    change_performer_user_id=USER_ID_1,
    change_target_user_id=USER_ID_1,
    create_date=CHANGE_DATE_2,
    create_user="admin",
    privilege_change_type_code="REMOVE",
    privilege_details=PRIVILEGE_DETAILS,
    application_id=APPLICATION_ID_2,
)

MOCKED_PERMISSION_HISTORY_RESPONSE = [
    PermissionAuditHistoryResDto(
        change_date="2024-09-11T12:00:00",
        change_performer_user_details={"username": "user1", "role": "admin"},
        change_performer_user_id=1,
        change_target_user_id=1,
        create_date="2024-09-11T12:00:00",
        create_user="admin",
        privilege_change_type_code="ADD",
        privilege_details={"role": "submitter"},
    )
]
