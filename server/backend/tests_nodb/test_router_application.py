import logging
import starlette.testclient
from api.app.main import apiPrefix
import time
from api.app.jwt_validation import ERROR_TOKEN_DECODE
from api.app.jwt_validation import ERROR_INVALID_CLIENT
from api.app.jwt_validation import ERROR_INVALID_ALGORITHM
from api.app.jwt_validation import ERROR_MISSING_KID
from api.app.jwt_validation import ERROR_NO_RSA_KEY
from api.app.jwt_validation import ERROR_EXPIRED_TOKEN
from api.app.jwt_validation import ERROR_CLAIMS
from api.app.jwt_validation import ERROR_VALIDATION
import json
from .utils import create_jwt_token, create_jwt_claims, assert_error_response
from Crypto.PublicKey import RSA

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"


def test_get_application_success(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    token = create_jwt_token(test_rsa_key)

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 204
    data = response.json()
    assert data == []


def test_get_application_no_authentication_failure(
        test_client_fixture: starlette.testclient.TestClient):

    response = test_client_fixture.get(endPoint)
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")

    assert response.status_code == 401
    assert json.loads(response.text)['detail'] == "Not authenticated"


def test_get_application_bad_token_failure(
        test_client_fixture: starlette.testclient.TestClient):

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": "Bearer 12345"})

    assert_error_response(response, 401, ERROR_TOKEN_DECODE)


def test_get_application_bad_client_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims['client_id'] = "incorrect"
    token = create_jwt_token(test_rsa_key, claims)

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert_error_response(response, 401, ERROR_INVALID_CLIENT)


def test_get_application_wrong_alg_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    invalid_algorithm = 'HS256'
    token = create_jwt_token(test_rsa_key, claims, invalid_algorithm)

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert_error_response(response, 401, ERROR_INVALID_ALGORITHM)


def test_get_application_missing_kid_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    token = create_jwt_token(test_rsa_key, test_headers={})

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert_error_response(response, 401, ERROR_MISSING_KID)


def test_get_application_missing_rsa_key_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key_missing):

    token = create_jwt_token(test_rsa_key_missing)

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert_error_response(response, 401, ERROR_NO_RSA_KEY)


def test_get_application_expired_token_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims['exp'] = time.time() - 60000
    token = create_jwt_token(test_rsa_key, claims)

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert_error_response(response, 401, ERROR_EXPIRED_TOKEN)


def test_get_application_bad_issuer_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims['iss'] = 'incorrect'
    token = create_jwt_token(test_rsa_key, claims)

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert_error_response(response, 401, ERROR_CLAIMS)
    assert json.loads(response.text)['detail']['description'] == 'Invalid issuer'


def test_get_application_invalid_signature_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    wrong_key = RSA.generate(2048)

    token = create_jwt_token(wrong_key.exportKey("PEM"))

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": f"Bearer {token}"})

    assert_error_response(response, 401, ERROR_VALIDATION)

