import logging
import time
from http.client import FORBIDDEN
from unittest.mock import MagicMock, Mock, patch

from api.app.constants import ERROR_CODE_INVALID_OPERATION
from api.app.crud import crud_application, crud_utils
from api.app.jwt_validation import (ERROR_EXPIRED_TOKEN,
                                    ERROR_PERMISSION_REQUIRED)
from api.app.main import app, external_v1_api_prefix
from fastapi import status
from fastapi.testclient import TestClient
from testspg import jwt_utils

LOGGER = logging.getLogger(__name__)

endPoint = f"{external_v1_api_prefix}/users"
client = TestClient(app)


# ------------------ test user_search ----------------------- #

def test_user_search_bearer_token_required(test_client_fixture: TestClient, test_rsa_key):
    # test request requires auth token to be authenticated to the API
    response = test_client_fixture.get(f"{endPoint}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # test request with expired token being checked
    claims = jwt_utils.create_jwt_claims()
    claims['exp'] = time.time() - 100000
    token = jwt_utils.create_jwt_token(test_rsa_key, claims=claims)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    jwt_utils.assert_error_response(response, 401, ERROR_EXPIRED_TOKEN)


def test_user_search_guards_by_authorize_ext_api_by_app_role(
    test_client_fixture: TestClient,
    auth_headers,
    override_depends__get_current_requester
):
    # test when api called with invalid app client id (application not found by app client id)
    override_depends__get_current_requester()
    with patch.object(crud_application, "get_application_by_app_client_id", return_value=None):
        response = test_client_fixture.get(f"{endPoint}", headers=auth_headers)
        jwt_utils.assert_error_response(response, FORBIDDEN, ERROR_CODE_INVALID_OPERATION)

    # test when requester does not have permission to access the API
    mock_app = MagicMock()
    mock_app.application_id = 123 # fake
    with patch.object(crud_application, "get_application_by_app_client_id", return_value=mock_app), \
        patch.object(crud_utils, "allow_ext_call_api_permission", return_value=False):
        response = test_client_fixture.get(f"{endPoint}", headers=auth_headers)
        jwt_utils.assert_error_response(response, FORBIDDEN, ERROR_PERMISSION_REQUIRED)
        assert "No permission to call" in response.json()["detail"]["description"]
