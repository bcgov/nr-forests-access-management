TEST_FOM_DEV_APPLICATION_ID = 2
TEST_FOM_TEST_APPLICATION_ID = 3

TEST_FOM_DEV_SUBMITTER_ROLE_ID = 3
TEST_FOM_DEV_REVIEWER_ROLE_ID = 4

TEST_FOM_TEST_REVIEWER_ROLE_ID = 8


TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE = {
    # todo: this might need to be a real idir username
    # once we enable the verifiy idir feature
    "user_name": "fom_user_test",
    "user_type_code": "I",
    "role_id": TEST_FOM_DEV_REVIEWER_ROLE_ID
}
TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT = {
    # todo: this might need to be a real test bceid username
    # once we enable the verifiy bceid feature
    "user_name": "fom_user_test",
    "user_type_code": "B",
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": "00000001"
}
TEST_USER_ROLE_ASSIGNMENT_FOM_TEST_CONCRETE = {
    # todo: this might need to be a real idir username
    # once we enable the verifiy idir feature
    "user_name": "fom_user_test",
    "user_type_code": "I",
    "role_id": TEST_FOM_TEST_REVIEWER_ROLE_ID
}
