TEST_FOM_DEV_APPLICATION_ID = 2
TEST_FOM_TEST_APPLICATION_ID = 3

TEST_FOM_DEV_SUBMITTER_ROLE_ID = 3
TEST_FOM_DEV_REVIEWER_ROLE_ID = 4

TEST_FOM_TEST_REVIEWER_ROLE_ID = 8

TEST_NOT_EXIST_ROLE_ID = 0
TEST_NOT_EXIST_APPLICATION_ID = 0

TEST_CREATOR = "TESTER"

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
    "user_type_code": "B",
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": "10000000"
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
