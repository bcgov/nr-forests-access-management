import logging
from http import HTTPStatus
import starlette.testclient

from api.app.main import apiPrefix
from api.app.constants import ERROR_CODE_INVALID_OPERATION
from api.app.jwt_validation import ERROR_GROUPS_REQUIRED
import testspg.jwt_utils as jwt_utils


LOGGER = logging.getLogger(__name__)
end_point = f"{apiPrefix}/user_terms_conditions"
validation_endpoint = f"{end_point}/user:validate"
COGNITO_USER_ID_LOAD_3_TEST = (
    "test-bceidbusiness_532905de0aa24923ae535428mangledf171bf13@bceidbusiness"
)


def test_validate_user_requires_accept_terms_and_conditions(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # this router test covers the crud method require_accept_terms_and_conditions

    # verify idir user does not need to accept terms and conditions
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.post(
        validation_endpoint, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == False

    # verify business bceid user has no delegated admin access in FAM does not need to accept terms and conditions
    token = jwt_utils.create_jwt_token(
        test_rsa_key, username=COGNITO_USER_ID_LOAD_3_TEST
    )
    response = test_client_fixture.post(
        validation_endpoint, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == False

    # verify user has no access in FAM cannot make this request
    token = jwt_utils.create_jwt_token(
        test_rsa_key, roles=[], username=COGNITO_USER_ID_LOAD_3_TEST
    )
    response = test_client_fixture.post(
        validation_endpoint, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["detail"].get("code") == ERROR_GROUPS_REQUIRED

    # verify business bceid delegated admin needs to accept terms and conditions
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    response = test_client_fixture.post(
        validation_endpoint, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == True

    # create user terms and conditions acceptance record for business bceid delegated admin
    response = test_client_fixture.post(end_point, headers=jwt_utils.headers(token))
    assert response.status_code == HTTPStatus.OK

    # verify the same business bceid delegated admin has no need to accept terms and conditions anymore
    response = test_client_fixture.post(
        validation_endpoint, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == False


def test_create_user_terms_and_conditions(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # creating user terms conditions record for business bceid delegated admin is tested in test_validate_user_requires_accept_terms_and_conditions

    # verify no need to create terms and conditions for IDIR user
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.post(end_point, headers=jwt_utils.headers(token))
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["detail"].get("code") == ERROR_CODE_INVALID_OPERATION

    # verify user has no access in FAM cannot make this request
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[])
    response = test_client_fixture.post(end_point, headers=jwt_utils.headers(token))
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["detail"].get("code") == ERROR_GROUPS_REQUIRED
