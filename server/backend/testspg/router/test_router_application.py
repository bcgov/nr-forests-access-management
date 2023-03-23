import logging
import starlette.testclient
from api.app.main import apiPrefix
import testspg.jwt_utils as jwt_utils

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"

TEST_APPLICATION_NAME_FOM_DEV = "FOM_DEV"
TEST_APPLICATION_ID_FOM_DEV = 2
TEST_APPLICATION_ROLES_FOM_DEV = ["FOM_SUBMITTER", "FOM_REVIEWER"]
TEST_APPLICATION_ROLE_ID_FOM_DEV = 3
TEST_APPLICATION_ID_NOT_FOUND = 0

ERROR_INVALID_APPLICATION_ID = "invalid_application_id"

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
    print('response1231121', response)
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
    role_end_point = endPoint + f"/{TEST_APPLICATION_ID_FOM_DEV}/fam_roles"
    access_roles_fom_dev_only = ["FOM_DEV_ACCESS_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(role_end_point, headers=jwt_utils.headers(token))
    data = response.json()
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
        print('app_role1234', app_role)
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
    assert data[0]["application_id"] == TEST_APPLICATION_ID_FOM_DEV
    assert data[0]["role_type_code"] == "A"
    assert data[1]["role_name"] == TEST_APPLICATION_ROLES_FOM_DEV[1]
    assert data[1]["application_id"] == TEST_APPLICATION_ID_FOM_DEV
    assert data[1]["role_type_code"] == "C"

    # todo: add test for parent_role_id for abstract role, need to add a role first
    # todo: add test for client_number_id for abstract role


def test_get_fam_application_user_role_assignment(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    role_assignment_end_point = endPoint + f"/{TEST_APPLICATION_ID_NOT_FOUND}/user_role_assignment"
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert data["detail"]["code"] == ERROR_INVALID_APPLICATION_ID

    role_assignment_end_point = endPoint + f"/{TEST_APPLICATION_ID_FOM_DEV}/user_role_assignment"
    access_roles_fom_dev_only = ["FOM_DEV_ACCESS_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 0  # initially no one is assigned with FOM_DEV roles

    # todo: add role assignment for fom dev and then verify the return
