import pytest
from fastapi.testclient import TestClient
from api.app.main import app, apiPrefix
from testspg import jwt_utils
from testspg.fixture.permission_audit_fixture import (
    APPLICATION_ID_1,
    USER_ID_1,
    MOCKED_PERMISSION_HISTORY_RESPONSE,
)

client = TestClient(app)
ENDPOINT_ROOT = "permission-audit-history"


@pytest.fixture(scope="function")
def auth_headers(test_rsa_key):
    token = jwt_utils.create_jwt_token(test_rsa_key)
    headers = jwt_utils.headers(token)
    return headers


# Test successful retrieval
def test_get_permission_audit_history_success(mocker, auth_headers):
    mocker.patch(
        "api.app.crud.crud_permission_audit.read_permission_audit_history_by_user_and_application",
        return_value=MOCKED_PERMISSION_HISTORY_RESPONSE,
    )

    response = client.get(
        f"{apiPrefix}/{ENDPOINT_ROOT}?user_id={USER_ID_1}&application_id={APPLICATION_ID_1}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["change_date"] == MOCKED_PERMISSION_HISTORY_RESPONSE[
        0
    ].change_date.isoformat().replace("+00:00", "Z")


# Test retrieval with no records
def test_get_permission_audit_history_bad_request(mocker, auth_headers):
    mocker.patch(
        "api.app.crud.crud_permission_audit.read_permission_audit_history_by_user_and_application",
        return_value=[],
    )

    response = client.get(
        f"{apiPrefix}/{ENDPOINT_ROOT}?user_id=999&application_id=999",
        headers=auth_headers,
    )

    assert response.status_code == 400


# Test handling of invalid user_id
def test_get_permission_audit_history_invalid_user_id_type(auth_headers):
    response = client.get(
        f"{apiPrefix}/{ENDPOINT_ROOT}?user_id=invalid_user_id&application_id={APPLICATION_ID_1}",
        headers=auth_headers,
    )

    assert response.status_code == 422


# Test unauthorized access
def test_get_permission_audit_history_unauthorized(mocker):
    mocker.patch(
        "api.app.routers.router_guards.authorize_by_app_id",
        side_effect=Exception("Unauthorized"),
    )

    response = client.get(
        f"{apiPrefix}/{ENDPOINT_ROOT}?user_id={USER_ID_1}&application_id={APPLICATION_ID_1}"
    )

    assert response.status_code == 403


# Test database dependency failure
def test_get_permission_audit_history_dependency_failure(mocker, auth_headers):
    mocker.patch(
        "api.app.database.get_db", side_effect=Exception("Database connection error")
    )

    response = client.get(
        f"{apiPrefix}/{ENDPOINT_ROOT}?user_id={USER_ID_1}&application_id={APPLICATION_ID_1}",
        headers=auth_headers,
    )

    assert response.status_code == 500
