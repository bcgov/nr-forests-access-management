import logging
import starlette.testclient
from api.app.main import apiPrefix
from .utils import create_jwt_token, create_jwt_claims, assert_error_response

from api.app.jwt_validation import ERROR_GROUPS_REQUIRED

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications/authorize"


def test_get_application_success(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    token = create_jwt_token(test_rsa_key)

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 204
    data = response.json()
    assert data == []


def test_get_application_missing_groups_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims.pop("cognito:groups")
    token = create_jwt_token(test_rsa_key, claims)

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)


def test_get_application_no_groups_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims["cognito:groups"] = []
    token = create_jwt_token(test_rsa_key, claims)

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)


