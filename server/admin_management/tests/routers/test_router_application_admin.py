import logging
from http import HTTPStatus

import starlette.testclient
import tests.jwt_utils as jwt_utils
from api.app.constants import (ERROR_CODE_INVALID_REQUEST_PARAMETER,
                               AdminRoleAuthGroup, UserType)
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.main import apiPrefix
from api.app.routers.router_application_admin import router
from api.app.routers.router_guards import (ERROR_INVALID_APPLICATION_ID,
                                           ERROR_NOT_ALLOWED_USER_TYPE,
                                           authorize_by_fam_admin)
from api.app.services.user_service import UserService
from tests.constants import (TEST_APPLICATION_NAME_FAM,
                             TEST_FOM_DEV_ADMIN_ROLE, TEST_INVALID_USER_TYPE,
                             TEST_NEW_APPLICATION_ADMIN,
                             TEST_NON_EXIST_ROLE_NAME,
                             TEST_NOT_EXIST_APPLICATION_ID)
from tests.test_data.application_admin_data import \
    APP_ADMIN_RESPONSE_SCHEMA_4_RECORDS
from tests.constants import TEST_APPLICATION_ID_FAM
from tests.test_data.mock_application_admins import MOCK_APPLICATION_ADMINS

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/application-admins"


def test_create_application_admin(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
    user_service: UserService
):
    # test create with invalid role
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.post(
        f"{endPoint}", json=TEST_NEW_APPLICATION_ADMIN, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

    # override router guard dependencies
    target_user_override = {
        **TEST_NEW_APPLICATION_ADMIN,
        "first_name": "test",
        "last_name": "app_admin",
        "email": "test_app_admin@test.com"
    }
    override_get_verified_target_user(target_user_override)

    # test create application admin
    token = jwt_utils.create_jwt_token(
        test_rsa_key
    )  # by deafult it will create with FAM admin role
    response = test_client_fixture.post(
        f"{endPoint}", json=TEST_NEW_APPLICATION_ADMIN, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert data.get("application_id") == TEST_NEW_APPLICATION_ADMIN.get(
        "application_id"
    )

    # also verify fam_user gets updated for first_name, last_name, email
    user = user_service.get_user_by_domain_and_name(
        TEST_NEW_APPLICATION_ADMIN.get("user_type_code"),
        TEST_NEW_APPLICATION_ADMIN.get("user_name")
    )
    assert user is not None
    assert user.user_id == data.get("user_id")
    assert user.first_name == target_user_override["first_name"]
    assert user.last_name == target_user_override["last_name"]
    assert user.email == target_user_override["email"]

    # test create duplicate application admin
    response = test_client_fixture.post(
        f"{endPoint}", json=TEST_NEW_APPLICATION_ADMIN, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() is not None
    assert str(response.json()["detail"]).find("User is admin already") != -1

    # test create with invalid user type
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **TEST_NEW_APPLICATION_ADMIN,
            "user_type_code": TEST_INVALID_USER_TYPE,
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.content is not None
    assert str(response.content).find("Input should be 'I' or 'B'") != -1

    # test not allowed user type, only allow IDIR
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **TEST_NEW_APPLICATION_ADMIN,
            "user_type_code": UserType.BCEID,
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == 400
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_NOT_ALLOWED_USER_TYPE) != -1

    # test create with non exists application id
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **TEST_NEW_APPLICATION_ADMIN,
            "application_id": TEST_NOT_EXIST_APPLICATION_ID,
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_INVALID_APPLICATION_ID) != -1


def test_delete_application_admin(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
):
    # override router guard dependencies
    override_get_verified_target_user(TEST_NEW_APPLICATION_ADMIN)

    # create an application admin first
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.post(
        f"{endPoint}", json=TEST_NEW_APPLICATION_ADMIN, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert data.get("application_id") == TEST_NEW_APPLICATION_ADMIN.get(
        "application_id"
    )

    # test delete with invalid role
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.delete(
        f"{endPoint}/{data['application_admin_id']}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

    # test delete application admin
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.delete(
        f"{endPoint}/{data['application_admin_id']}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK

    # test delete non exists application admin
    response = test_client_fixture.delete(
        f"{endPoint}/{data['application_admin_id']}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert response.json()["detail"]["code"] == ERROR_CODE_INVALID_REQUEST_PARAMETER


def test_get_application_admins(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # Test no token. Receive 401
    response = test_client_fixture.get(f"{endPoint}")
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    # Test invalid role. (Only FAM admin role is allowed) Receive 403
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

    # Test valid role (FAM_ADMIN) can get applications
    token = jwt_utils.create_jwt_token(test_rsa_key, [AdminRoleAuthGroup.FAM_ADMIN])
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))

    assert response.status_code == 200

    data = response.json()
    assert len(data) != 0
    # - Verify following keys are in return.
    assert "application_admin_id" in data[0].keys()
    assert "user_id" in data[0].keys()
    assert "application_id" in data[0].keys()
    assert "user" in data[0].keys()
    assert "application" in data[0].keys()
    # - Verify list contains application admin for "FAM"
    assert any(TEST_APPLICATION_NAME_FAM in x["application"].values() for x in data)

def test_export_application_admins_success(
    mocker,
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    mocker.patch(
        "api.app.routers.router_application_admin.ApplicationAdminService.get_application_admins",
        return_value=APP_ADMIN_RESPONSE_SCHEMA_4_RECORDS,
    )

    token = jwt_utils.create_jwt_token(test_rsa_key, [AdminRoleAuthGroup.FAM_ADMIN])
    response = test_client_fixture.get(f"{endPoint}/export", headers=jwt_utils.headers(token))

    assert response.status_code == HTTPStatus.OK
    assert "text/csv" in response.headers["Content-Type"].lower()
    assert "Content-Disposition" in response.headers
    assert response.headers["Content-Disposition"].startswith("attachment; filename=")
    filename = response.headers["Content-Disposition"].split("=")[1]
    assert filename.endswith(".csv")
    assert response.content is not None

def test_export_application_admins_no_data(
    mocker,
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    mocker.patch(
        "api.app.routers.router_application_admin.ApplicationAdminService.get_application_admins",
        return_value=[],
    )

    token = jwt_utils.create_jwt_token(test_rsa_key, [AdminRoleAuthGroup.FAM_ADMIN])
    response = test_client_fixture.get(f"{endPoint}/export", headers=jwt_utils.headers(token))

    assert response.status_code == HTTPStatus.OK
    assert "text/csv" in response.headers["Content-Type"].lower()
    assert "Content-Disposition" in response.headers
    assert response.headers["Content-Disposition"].startswith("attachment; filename=")
    filename = response.headers["Content-Disposition"].split("=")[1]
    assert filename.endswith(".csv")
    assert response.content is not None
    assert b"User Name" not in response.content  # No data in CSV

def test_export_application_admins_no_data_unauthorized(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    """
    Test the export_application_admins endpoint for unauthorized access.
    """
    unauthorized_token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_NON_EXIST_ROLE_NAME])

    response = test_client_fixture.get(f"{endPoint}/export", headers=jwt_utils.headers(unauthorized_token))

    assert response.status_code == HTTPStatus.FORBIDDEN

def test_export_application_admins_has_necessary_authorizeaton_guard_checks():
    """
    Test the export_application_admins endpoint has authorization guards in place.
    This test verifies that the endpoint is protected by the 'authorize_by_fam_admin' dependencie.
    """
    route = next(
        (route for route in router.routes if route.path == "/export"),
        None,
    )
    assert route is not None
    assert any(
        dependency.dependency == authorize_by_fam_admin for dependency in route.dependencies
    ), "authorize_by_fam_admin check should be a dependency for export_application_admins"

def test_get_application_admins_by_application_id(mocker, test_client_fixture, test_rsa_key):
    """
    Test GET /application-admins/application/{application_id} returns expected data and 200 status.
    """
    # Use a valid application ID that exists in test database
    # Mock the application service to return a valid application (required by authorize_by_app_id guard)
    mock_application = mocker.MagicMock()
    mock_application.application_name = "FAM"
    mock_application.application_id = TEST_APPLICATION_ID_FAM
    mocker.patch(
        "api.app.routers.router_application_admin.ApplicationService.get_application",
        return_value=mock_application,
    )

    # Mock the application admin service to return known data
    mocker.patch(
        "api.app.routers.router_application_admin.ApplicationAdminService.get_application_admins_by_application_id",
        return_value=[MOCK_APPLICATION_ADMINS[0]],
    )

    application_id = TEST_APPLICATION_ID_FAM
    token = jwt_utils.create_jwt_token(test_rsa_key, [AdminRoleAuthGroup.FAM_ADMIN])

    # Act: Make the GET request
    response = test_client_fixture.get(
        f"{endPoint}/application/{application_id}",
        headers=jwt_utils.headers(token)
    )

    # Assert: Check response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "application_admin_id" in data[0]
    assert "user_id" in data[0]
    assert "application_id" in data[0]
    assert "user" in data[0]
    assert "application" in data[0]
    assert data[0]["application_admin_id"] == MOCK_APPLICATION_ADMINS[0]["application_admin_id"]

# This test checks if the endpoint returns 400 when the application ID is invalid
def test_get_application_admins_by_application_id_app_not_found(mocker, test_client_fixture, test_rsa_key):
    """
    Test GET /application-admins/application/{application_id} returns 400 if application does not exist.
    """
    mocker.patch(
        "api.app.routers.router_application_admin.ApplicationService.get_application",
        return_value=None,
    )
    application_id = 9999  # Non-existent
    token = jwt_utils.create_jwt_token(test_rsa_key, [AdminRoleAuthGroup.FAM_ADMIN])
    response = test_client_fixture.get(
        f"{endPoint}/application/{application_id}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 400
    assert "Application ID" in response.text

# This test checks if the endpoint returns 403 when the user lacks the required role
def test_get_application_admins_by_application_id_forbidden(mocker, test_client_fixture, test_rsa_key):
    """
    Test GET /application-admins/application/{application_id} returns 403 if user lacks required role.
    """
    from tests.constants import TEST_APPLICATION_ID_FAM
    mock_application = mocker.MagicMock()
    mock_application.application_name = "FAM"
    mock_application.application_id = TEST_APPLICATION_ID_FAM
    mocker.patch(
        "api.app.routers.router_application_admin.ApplicationService.get_application",
        return_value=mock_application,
    )
    token = jwt_utils.create_jwt_token(test_rsa_key, ["SOME_OTHER_ROLE"])
    response = test_client_fixture.get(
        f"{endPoint}/application/{TEST_APPLICATION_ID_FAM}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 403
    assert "Operation requires role" in response.text
