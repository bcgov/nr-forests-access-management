import logging
import starlette.testclient
from api.app.main import apiPrefix
from time import time
from api.app.jwt_validation import ERROR_TOKEN_DECODE
import json
from .utils import create_jwt_token, create_jwt_claims

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"


def test_get_application_noauthentication_failure(
        test_client_fixture: starlette.testclient.TestClient):
    response = test_client_fixture.get(endPoint)
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")

    assert response.status_code == 401
    assert json.loads(response.text)['detail'] == "Not authenticated"


def test_get_application_bad_token_failure(
        test_client_fixture: starlette.testclient.TestClient):

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": "Bearer 12345"})

    assert response.status_code == 401
    assert json.loads(response.text)['detail'] == ERROR_TOKEN_DECODE


def test_get_application_success(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    token = create_jwt_token(test_rsa_key, create_jwt_claims())

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 204
    data = response.json()
    assert data == []

# test_get_application_bad_client
# def test_get_application_invalid_signature_failure
# def test_get_application_bad_issuer
# def test_get_application_bad_client
# def test_get_application_wrong_alg
# def test_get_application_missing_kid
