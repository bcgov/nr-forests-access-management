import logging
from http import HTTPStatus

import starlette.testclient
import testspg.jwt_utils as jwt_utils
from api.app.main import apiPrefix
from api.app.constants import ERROR_CODE_INVALID_APPLICATION_ID
from testspg.constants import (
    CLIENT_NUMBER_EXISTS_ACTIVE_00000001,
    TEST_FOM_DEV_APPLICATION_ID,
    USERR_ASGNMNT_FOM_DEV_AR_00000001_BCEID,
    USERR_ASGNMNT_FOM_DEV_AR_00001018_BCEID_L3T,
    USERR_ASGNMNT_FOM_DEV_AR_00001018_BCEID_L4T,
    USERR_ASGNMNT_FOM_DEV_AR_00000001_IDIR,
    USERR_ASGNMNT_FOM_DEV_CR_BCEID_L3T,
    USERR_ASGNMNT_FOM_DEV_CR_BCEID_L4T,
    USERR_ASGNMNT_FOM_DEV_CR_IDIR,
    USERR_ASGNMNT_FOM_TEST_AR_00001018_BCEID_L4T,
    USERR_ASGNMNT_FOM_TEST_CR_BCEID_L3T,
    USER_NAME_BCEID_LOAD_4_TEST)

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"

TEST_APPLICATION_NAME_FOM_DEV = "FOM_DEV"
TEST_APPLICATION_ROLES_FOM_DEV = ["FOM_SUBMITTER", "FOM_REVIEWER"]
TEST_APPLICATION_ID_NOT_FOUND = 0


def test_get_applications(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    # Test Accss Roles: FAM_ADMIN only
    access_roles_fam_only = ["FAM_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fam_only)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["application_name"] == "FAM"

    # Test Accss Roles: FOM_DEV_ADMIN only
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["application_name"] == "FOM_DEV"

    # Test Accss Roles: both FAM_ADMIN and FOM_DEV_ADMIN
    access_roles_fam_fom_dev = ["FAM_ADMIN", "FOM_DEV_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fam_fom_dev)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 2
    assert data[0]["application_name"] == "FAM"
    assert data[1]["application_name"] == "FOM_DEV"
    # verify it got all attributes
    for app in data:
        assert "application_id" in app
        assert "application_name" in app
        assert "application_description" in app
        assert "create_user" in app
        assert "create_date" in app
        assert "update_user" in app
        assert "update_date" in app
        assert "app_environment" in app

    # Test Accss Roles: on NO_APP_ADMIN
    access_roles_no_app = ["NO_APP_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_no_app)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 0


def test_get_fam_application_roles(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    # create a concrete role with an abstract role as parent
    # this role won't be returned
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)

    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=USERR_ASGNMNT_FOM_DEV_AR_00000001_BCEID,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200

    role_end_point = endPoint + f"/{TEST_FOM_DEV_APPLICATION_ID}/fam_roles"
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(role_end_point, headers=jwt_utils.headers(token))
    data = response.json()
    # only return roles without a parent role
    assert len(data) == 2

    for app_role in data:
        assert "role_id" in app_role
        assert "role_name" in app_role
        assert "role_purpose" in app_role
        assert "parent_role_id" in app_role
        assert "application_id" in app_role
        assert "forest_client_number" in app_role
        assert "client_number" in app_role
        assert "role_type_code" in app_role

    fom_reviewer_role_found = False
    fom_submitter_role_found = False

    for datum in data:
        if (
            datum["role_name"] == TEST_APPLICATION_ROLES_FOM_DEV[0]
            and datum["application_id"] == TEST_FOM_DEV_APPLICATION_ID
            and datum["role_type_code"] == "A"
        ):
            fom_submitter_role_found = True
        elif (
            datum["role_name"] == TEST_APPLICATION_ROLES_FOM_DEV[1]
            and datum["application_id"] == TEST_FOM_DEV_APPLICATION_ID
            and datum["role_type_code"] == "C"
        ):
            fom_reviewer_role_found = True

    assert fom_submitter_role_found, f"Expected role {TEST_APPLICATION_ROLES_FOM_DEV[0]} in results"
    assert fom_reviewer_role_found, f"Expected role {TEST_APPLICATION_ROLES_FOM_DEV[1]} in results"


def test_get_fam_application_user_role_assignment_no_matching_application(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    role_assignment_end_point = endPoint + \
        f"/{TEST_APPLICATION_ID_NOT_FOUND}/user_role_assignment"
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert data["detail"]["code"] == ERROR_CODE_INVALID_APPLICATION_ID


def test_get_fam_application_user_role_assignment_no_role_assignments(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]

    # test no user role assignment for the application
    role_assignment_end_point = endPoint + \
        f"/{TEST_FOM_DEV_APPLICATION_ID}/user_role_assignment"
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 0  # initially no one is assigned with FOM_DEV roles


def test_get_fam_application_user_role_assignment_concrete_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]

    role_assignment_end_point = endPoint + \
        f"/{TEST_FOM_DEV_APPLICATION_ID}/user_role_assignment"

    # test user role assignment
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=USERR_ASGNMNT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    concrete_role_data = response.json()

    # check
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_role_xref_id"] == concrete_role_data["user_role_xref_id"]
    assert data[0]["user"]["user_type_code"] \
        == USERR_ASGNMNT_FOM_DEV_CR_IDIR["user_type_code"]
    assert data[0]["user"]["user_name"] \
        == USERR_ASGNMNT_FOM_DEV_CR_IDIR["user_name"]
    assert data[0]["role"]["role_type_code"] == "C"
    assert data[0]["role"]["role_name"] == "FOM_REVIEWER"


def test_get_fam_application_user_role_assignment_abstract_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]

    role_assignment_end_point = endPoint + \
        f"/{TEST_FOM_DEV_APPLICATION_ID}/user_role_assignment"

    # test user role assignment for abstract role
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=USERR_ASGNMNT_FOM_DEV_AR_00000001_BCEID,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    abstract_role_data = response.json()

    # check
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_role_xref_id"] == abstract_role_data["user_role_xref_id"]
    assert data[0]["user"]["user_type_code"] \
        == USERR_ASGNMNT_FOM_DEV_AR_00000001_BCEID["user_type_code"]
    assert data[0]["user"]["user_name"] \
        == USERR_ASGNMNT_FOM_DEV_AR_00000001_BCEID["user_name"]
    assert data[0]["role"]["role_type_code"] == "C"
    assert data[0]["role"]["role_name"] == "FOM_SUBMITTER" + "_" + \
        USERR_ASGNMNT_FOM_DEV_AR_00000001_BCEID["forest_client_number"]
    assert data[0]["role"]["parent_role"]["role_type_code"] == "A"
    assert data[0]["role"]["parent_role"]["role_name"] == "FOM_SUBMITTER"


def test_fam_application_endpoints_invlid_path_application_id_type(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    token = jwt_utils.create_jwt_token(test_rsa_key)
    # endpoint path /{application_id} should be int type, provided as invalid str type.
    invalid_path_param = "not-int-str-application-id"
    invalid_path_router_msg = "Input should be a valid integer"

    # endpont GET: /{application_id}/fam_roles
    application_role_endpoint = endPoint + f"/{invalid_path_param}/fam_roles"
    response = test_client_fixture.get(
        application_role_endpoint,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert invalid_path_router_msg in response.text

    # endpont GET: /{application_id}/user_role_assignment
    application_role_assignment_endpoint = endPoint + \
        f"/{invalid_path_param}/user_role_assignment"
    response = test_client_fixture.get(
        application_role_assignment_endpoint,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert invalid_path_router_msg in response.text


# ---------------- Test get application user role assignment filtering scenarios ------------ #

# TODO: in progress...
def test_get_application_user_assignments_filtering_for_delegated_admin(
    create_test_user_role_assignments,
    fom_dev_access_admin_token,
    fom_test_access_admin_token
):
    # --- Create users at FOM_DEV (IDIR/BCEID, business organizations, etc...)
    # --- and verify different visibility scenarios.

    # --- Prepare
    # Assign IDIR test user to FOM_DEV app: FOM_REVIEWER and FOM_SUBMITTER role.
    configured_fom_dev_idir_users = [
        USERR_ASGNMNT_FOM_DEV_CR_IDIR,  # FOM_REVIEWER
        USERR_ASGNMNT_FOM_DEV_AR_00000001_IDIR   # FOM_SUBMITTER
    ]
    # Assign BCEID users to FOM_DEV app: FOM_REVIEWER role.
    # Two users (LOAD-3-TEST, LOAD-4-TEST) belong to two different organizations.
    configured_fom_dev_bceid_reviewers = [
        USERR_ASGNMNT_FOM_DEV_CR_BCEID_L3T,  # BCEID user (org 1)
        USERR_ASGNMNT_FOM_DEV_CR_BCEID_L4T   # BCEID user (org 2)
    ]
    # Assign BCEID users (LOAD-3-TEST, LOAD-4-TEST) to FOM_DEV FOM_SUBMITTER
    #   with the same role (forest client: 00001018)
    # Two users (LOAD-3-TEST, LOAD-4-TEST) belong to two different organizations.
    configured_fom_dev_bceid_submitter_00001018 = [
        USERR_ASGNMNT_FOM_DEV_AR_00001018_BCEID_L3T,
        USERR_ASGNMNT_FOM_DEV_AR_00001018_BCEID_L4T
    ]
    # Also only assign BCEID user (LOAD-3-TEST) to FOM_DEV FOM_SUBMITTER with forest client 00001011
    USER_ROLE_ASGNMNT_FOM_DEV_ABSTRACT_BCEID_L3T_FC2 = \
        dict(USERR_ASGNMNT_FOM_DEV_AR_00001018_BCEID_L3T)
    USER_ROLE_ASGNMNT_FOM_DEV_ABSTRACT_BCEID_L3T_FC2["forest_client_number"] = CLIENT_NUMBER_EXISTS_ACTIVE_00000001

    # Additional BCEID users
    configured_fom_test_bceid_users = [
        USERR_ASGNMNT_FOM_TEST_CR_BCEID_L3T,  # BCEID user (org 1) FOM_REVIEWER
        USERR_ASGNMNT_FOM_TEST_AR_00001018_BCEID_L4T  # BCEID user (org 2) FOM_SUBMITTER
    ]

    # # --- Create
    # fom_dev_idir_users_assignments = create_test_user_role_assignments(
    #     fom_dev_access_admin_token, assigned_fom_dev_idir_users
    # )

    # fom_dev_bceid_reviewers_assignments = create_test_user_role_assignments(
    #     fom_dev_access_admin_token, assigned_fom_dev_bceid_reviewers
    # )

    # fom_dev_bceid_submitter_00001018_assignments = create_test_user_role_assignments(
    #     fom_dev_access_admin_token, assigned_fom_dev_bceid_submitter_00001018
    # )
    # # FOM_TEST:
    # fom_dev_bceid_submitter_00001011_assignments = create_test_user_role_assignments(
    #     fom_dev_access_admin_token, [TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT_BCEID_L3T_FC2]
    # )


    # fom_test_bceid_reviewers_assignments = create_test_user_role_assignments(
    #     fom_test_access_admin_token, assigned_fom_test_bceid_users
    # )


    # --- Verify


    # APP_ADMIN
    #     get_role_assignment_end_point = endPoint + \
    #    f"/{TEST_FOM_DEV_APPLICATION_ID}/user_role_assignment"
    # access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]
    # token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    # # check
    # response = test_client_fixture.get(role_assignment_end_point,
    #                                  headers=jwt_utils.headers(token))
    # data = response.json()
    # assert len(data) == 1
    # assert data[0]["user_role_xref_id"] == concrete_role_data["user_role_xref_id"]
    # assert data[0]["user"]["user_type_code"] \
    #     == TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE_IDIR["user_type_code"]
    # assert data[0]["user"]["user_name"] \
    #     == TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE_IDIR["user_name"]
    # assert data[0]["role"]["role_type_code"] == "C"
    # assert data[0]["role"]["role_name"] == "FOM_REVIEWER"





















































