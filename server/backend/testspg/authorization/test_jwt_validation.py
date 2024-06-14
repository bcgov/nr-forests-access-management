import json
import logging
import time

import starlette.testclient
from api.app.jwt_validation import (ERROR_CLAIMS, ERROR_EXPIRED_TOKEN,
                                    ERROR_INVALID_ALGORITHM,
                                    ERROR_INVALID_CLIENT, ERROR_MISSING_KID,
                                    ERROR_NO_RSA_KEY, ERROR_TOKEN_DECODE,
                                    JWT_CLIENT_ID_KEY)
from api.app.main import apiPrefix
from Crypto.PublicKey import RSA
from testspg.constants import FAM_APPLICATION_ID
from testspg.jwt_utils import (assert_error_response, create_jwt_claims,
                               create_jwt_token, headers)

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications/{FAM_APPLICATION_ID}/user_role_assignment"


def test_get_application_user_role_assignment_success(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    token = create_jwt_token(test_rsa_key)

    response = test_client_fixture.get(f"{endPoint}", headers=headers(token))

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_application_user_role_assignment_no_authentication_failure(
        test_client_fixture_unit: starlette.testclient.TestClient):

    response = test_client_fixture_unit.get(endPoint)

    assert response.status_code == 401
    assert json.loads(response.text)['detail'] == "Not authenticated"


def test_get_application_user_role_assignment_bad_token_failure(
        test_client_fixture_unit: starlette.testclient.TestClient):

    response = test_client_fixture_unit.get(f"{endPoint}", headers=headers("12345"))

    assert_error_response(response, 401, ERROR_TOKEN_DECODE)


def test_get_application_user_role_assignment_wrong_alg_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key):

    invalid_algorithm = 'HS256'
    token = create_jwt_token(test_rsa_key, test_algorithm=invalid_algorithm)

    response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

    assert_error_response(response, 401, ERROR_INVALID_ALGORITHM)


def test_get_application_user_role_assignment_missing_kid_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key):

    token = create_jwt_token(test_rsa_key, test_headers={})

    response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

    assert_error_response(response, 401, ERROR_MISSING_KID)


def test_get_application_user_role_assignment_missing_rsa_key_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key_missing):

    token = create_jwt_token(test_rsa_key_missing)

    response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

    assert_error_response(response, 401, ERROR_NO_RSA_KEY)


def test_get_application_user_role_assignment_bad_client_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims[JWT_CLIENT_ID_KEY] = "incorrect"
    token = create_jwt_token(test_rsa_key, claims=claims)

    response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

    assert_error_response(response, 401, ERROR_INVALID_CLIENT)


def test_get_application_user_role_assignment_expired_token_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims['exp'] = time.time() - 60000
    token = create_jwt_token(test_rsa_key, claims=claims)

    response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

    assert_error_response(response, 401, ERROR_EXPIRED_TOKEN)


def test_get_application_user_role_assignment_bad_issuer_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims['iss'] = 'incorrect'
    token = create_jwt_token(test_rsa_key, claims=claims)

    response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

    assert_error_response(response, 401, ERROR_CLAIMS)
    assert json.loads(response.text)['detail']['description'] == 'Invalid issuer'


def test_get_application_user_role_assignment_invalid_signature_failure(
        test_client_fixture_unit: starlette.testclient.TestClient):

    wrong_key = RSA.generate(2048)

    token = create_jwt_token(wrong_key.exportKey("PEM"))

    response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

    assert_error_response(response, 401, ERROR_CLAIMS)
