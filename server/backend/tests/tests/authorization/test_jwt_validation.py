# import logging
# import starlette.testclient
# import mock
# from api.app.main import apiPrefix
# from api.app.models import model as models
# from api.app import database
# import time
# from api.app.jwt_validation import (ERROR_TOKEN_DECODE,
#                                     ERROR_INVALID_CLIENT,
#                                     ERROR_INVALID_ALGORITHM,
#                                     ERROR_MISSING_KID,
#                                     ERROR_NO_RSA_KEY,
#                                     ERROR_EXPIRED_TOKEN,
#                                     ERROR_CLAIMS,
#                                     ERROR_VALIDATION,
#                                     JWT_CLIENT_ID_KEY)
# import json
# from jwt_utils import (create_jwt_token,
#                        create_jwt_claims,
#                        assert_error_response,
#                        headers)
# from Crypto.PublicKey import RSA
# from mock_alchemy.mocking import UnifiedAlchemyMagicMock

# LOGGER = logging.getLogger(__name__)
# endPoint = f"{apiPrefix}/fam_applications"


# def test_get_application_success(
#         test_client_fixture_unit: starlette.testclient.TestClient,
#         test_rsa_key):

#     test_client_fixture_unit.app.dependency_overrides[database.get_db] = \
#         lambda: UnifiedAlchemyMagicMock(data=[
#             (
#                 [mock.call.query(models.FamApplication), mock.call.all()], []
#             ),
#         ])

#     token = create_jwt_token(test_rsa_key)

#     response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

#     assert response.status_code == 204
#     data = response.json()
#     assert data == []


# def test_get_application_no_authentication_failure(
#         test_client_fixture_unit: starlette.testclient.TestClient):

#     response = test_client_fixture_unit.get(endPoint)

#     assert response.status_code == 401
#     assert json.loads(response.text)['detail'] == "Not authenticated"


# def test_get_application_bad_token_failure(
#         test_client_fixture_unit: starlette.testclient.TestClient):

#     response = test_client_fixture_unit.get(f"{endPoint}", headers=headers("12345"))

#     assert_error_response(response, 401, ERROR_TOKEN_DECODE)


# def test_get_application_bad_client_failure(
#         test_client_fixture_unit: starlette.testclient.TestClient,
#         test_rsa_key):

#     claims = create_jwt_claims()
#     claims[JWT_CLIENT_ID_KEY] = "incorrect"
#     token = create_jwt_token(test_rsa_key, claims)

#     response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

#     assert_error_response(response, 401, ERROR_INVALID_CLIENT)


# def test_get_application_wrong_alg_failure(
#         test_client_fixture_unit: starlette.testclient.TestClient,
#         test_rsa_key):

#     claims = create_jwt_claims()
#     invalid_algorithm = 'HS256'
#     token = create_jwt_token(test_rsa_key, claims, invalid_algorithm)

#     response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

#     assert_error_response(response, 401, ERROR_INVALID_ALGORITHM)


# def test_get_application_missing_kid_failure(
#         test_client_fixture_unit: starlette.testclient.TestClient,
#         test_rsa_key):

#     token = create_jwt_token(test_rsa_key, test_headers={})

#     response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

#     assert_error_response(response, 401, ERROR_MISSING_KID)


# def test_get_application_missing_rsa_key_failure(
#         test_client_fixture_unit: starlette.testclient.TestClient,
#         test_rsa_key_missing):

#     token = create_jwt_token(test_rsa_key_missing)

#     response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

#     assert_error_response(response, 401, ERROR_NO_RSA_KEY)


# def test_get_application_expired_token_failure(
#         test_client_fixture_unit: starlette.testclient.TestClient,
#         test_rsa_key):

#     claims = create_jwt_claims()
#     claims['exp'] = time.time() - 60000
#     token = create_jwt_token(test_rsa_key, claims)

#     response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

#     assert_error_response(response, 401, ERROR_EXPIRED_TOKEN)


# def test_get_application_bad_issuer_failure(
#         test_client_fixture_unit: starlette.testclient.TestClient,
#         test_rsa_key):

#     claims = create_jwt_claims()
#     claims['iss'] = 'incorrect'
#     token = create_jwt_token(test_rsa_key, claims)

#     response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

#     assert_error_response(response, 401, ERROR_CLAIMS)
#     assert json.loads(response.text)['detail']['description'] == 'Invalid issuer'


# def test_get_application_invalid_signature_failure(
#         test_client_fixture_unit: starlette.testclient.TestClient,
#         test_rsa_key):

#     wrong_key = RSA.generate(2048)

#     token = create_jwt_token(wrong_key.exportKey("PEM"))

#     response = test_client_fixture_unit.get(f"{endPoint}", headers=headers(token))

#     assert_error_response(response, 401, ERROR_VALIDATION)

