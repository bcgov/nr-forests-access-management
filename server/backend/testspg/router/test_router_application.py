import logging
import starlette.testclient
from api.app.main import apiPrefix
from api.app.jwt_validation import ERROR_INVALID_APPLICATION_ID
import testspg.jwt_utils as jwt_utils
from testspg.constants import TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE, \
    TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT, \
    TEST_FOM_DEV_APPLICATION_ID

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"

TEST_APPLICATION_NAME_FOM_DEV = "FOM_DEV"
TEST_APPLICATION_ROLES_FOM_DEV = ["FOM_SUBMITTER", "FOM_REVIEWER"]
TEST_APPLICATION_ID_NOT_FOUND = 0


def test_get_applications(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
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
    test_rsa_key
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
    xref_id = response.json()["user_role_xref_id"]

    role_end_point = endPoint + f"/{TEST_FOM_DEV_APPLICATION_ID}/fam_roles"
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(role_end_point, headers=jwt_utils.headers(token))
    data = response.json()
    # only return roles without a parent role
    assert len(data) == 2

    for app_role in data:
        # return example: how we define what to return?
        # the model has more columns
        # {'role_name': 'FOM_SUBMITTER',
        # 'role_purpose': 'Provides the privilege to submit a FOM (on behalf of a specific forest client)',
        # 'parent_role_id': None,
        # 'application_id': 2,
        # 'forest_client_number': None,
        # 'role_type_code': 'A',
        # 'client_number': None,
        # 'role_id': 3}
        assert "role_id" in app_role
        assert "role_name" in app_role
        assert "role_purpose" in app_role
        assert "parent_role_id" in app_role
        assert "application_id" in app_role
        # assert "client_number_id" in app_role
        # assert "create_user" in app_role
        # assert "create_date" in app_role
        # assert "update_user" in app_role
        # assert "update_date" in app_role
        assert "role_type_code" in app_role

    assert data[0]["role_name"] == TEST_APPLICATION_ROLES_FOM_DEV[0]
    assert data[0]["application_id"] == TEST_FOM_DEV_APPLICATION_ID
    assert data[0]["role_type_code"] == "A"
    assert data[1]["role_name"] == TEST_APPLICATION_ROLES_FOM_DEV[1]
    assert data[1]["application_id"] == TEST_FOM_DEV_APPLICATION_ID
    assert data[1]["role_type_code"] == "C"

    # cleanup
    response = test_client_fixture.delete(
        f"{apiPrefix}/user_role_assignment/{xref_id}",
        headers=jwt_utils.headers(token)
    )


def test_get_fam_application_user_role_assignment(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    access_roles_fom_dev_only = ["FOM_DEV_ACCESS_ADMIN"]

    # test get user role assignment for application not exists
    role_assignment_end_point = endPoint + \
        f"/{TEST_APPLICATION_ID_NOT_FOUND}/user_role_assignment"
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert data["detail"]["code"] == ERROR_INVALID_APPLICATION_ID

    # test no user role assignment for the application
    role_assignment_end_point = endPoint + \
        f"/{TEST_FOM_DEV_APPLICATION_ID}/user_role_assignment"
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 0  # initially no one is assigned with FOM_DEV roles

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

    # cleanup
    response = test_client_fixture.delete(
        f"{apiPrefix}/user_role_assignment/{concrete_role_data['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204

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

    # cleanup
    response = test_client_fixture.delete(
        f"{apiPrefix}/user_role_assignment/{abstract_role_data['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204
