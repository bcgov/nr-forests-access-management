import logging

import starlette.testclient
import testspg.jwt_utils as jwt_utils
from api.app.jwt_validation import ERROR_INVALID_APPLICATION_ID
from api.app.main import apiPrefix
from testspg.constants import (TEST_FOM_DEV_APPLICATION_ID,
                               TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
                               TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE)

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"

TEST_APPLICATION_NAME_FOM_DEV = "FOM_DEV"
TEST_APPLICATION_ROLES_FOM_DEV = ["FOM_SUBMITTER", "FOM_REVIEWER"]
TEST_APPLICATION_ID_NOT_FOUND = 0


def test_get_applications(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    db_pg_session
):
    # Test Accss Roles: FAM_ACCESS_ADMIN only
    access_roles_fam_only = ["FAM_ACCESS_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fam_only)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["application_name"] == "FAM"

    # Test Accss Roles: FOM_DEV_ACCESS_ADMIN only
    access_roles_fom_dev_only = ["FOM_DEV_ACCESS_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["application_name"] == "FOM_DEV"

    # Test Accss Roles: both FAM_ACCESS_ADMIN and FOM_DEV_ACCESS_ADMIN
    access_roles_fam_fom_dev = ["FAM_ACCESS_ADMIN", "FOM_DEV_ACCESS_ADMIN"]
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

    # Test Accss Roles: on NO_APP_ACCESS_ADMIN
    access_roles_no_app = ["NO_APP_ACCESS_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_no_app)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 0


def test_get_fam_application_roles(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    db_pg_session
):
    # create a concrete role with an abstract role as parent
    # this role won't be returned
    access_roles_fom_dev_only = ["FOM_DEV_ACCESS_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)

    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
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
    test_rsa_key,
    db_pg_session
):
    role_assignment_end_point = endPoint + \
        f"/{TEST_APPLICATION_ID_NOT_FOUND}/user_role_assignment"
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert data["detail"]["code"] == ERROR_INVALID_APPLICATION_ID


def test_get_fam_application_user_role_assignment_no_role_assignments(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    db_pg_session
):
    access_roles_fom_dev_only = ["FOM_DEV_ACCESS_ADMIN"]

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
    test_rsa_key,
    db_pg_session
):
    access_roles_fom_dev_only = ["FOM_DEV_ACCESS_ADMIN"]

    role_assignment_end_point = endPoint + \
        f"/{TEST_FOM_DEV_APPLICATION_ID}/user_role_assignment"

    # test user role assignment
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
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
        == TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE["user_type_code"]
    assert data[0]["user"]["user_name"] \
        == TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE["user_name"]
    assert data[0]["role"]["role_type_code"] == "C"
    assert data[0]["role"]["role_name"] == "FOM_REVIEWER"


def test_get_fam_application_user_role_assignment_abstract_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    db_pg_session
):
    access_roles_fom_dev_only = ["FOM_DEV_ACCESS_ADMIN"]

    role_assignment_end_point = endPoint + \
        f"/{TEST_FOM_DEV_APPLICATION_ID}/user_role_assignment"

    # test user role assignment for abstract role
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
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
        == TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT["user_type_code"]
    assert data[0]["user"]["user_name"] \
        == TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT["user_name"]
    assert data[0]["role"]["role_type_code"] == "C"
    assert data[0]["role"]["role_name"] == "FOM_SUBMITTER" + "_" + \
        TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT["forest_client_number"]
    assert data[0]["role"]["parent_role"]["role_type_code"] == "A"
    assert data[0]["role"]["parent_role"]["role_name"] == "FOM_SUBMITTER"

