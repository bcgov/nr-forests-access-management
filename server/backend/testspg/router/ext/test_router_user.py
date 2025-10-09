import logging
import time
from contextlib import contextmanager
from http.client import FORBIDDEN
from unittest.mock import MagicMock, patch

import pytest
from api.app.constants import (ERROR_CODE_INVALID_OPERATION,
                               EXT_DEFAULT_PAGE_SIZE, EXT_MIN_PAGE)
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

mock_app = MagicMock()
mock_app.application_id = 123 # fake
mock_search_empty_result = {
    "meta": {"total": 0,"pageCount": 0, "page": 1, "size": 10},
    "users": []}
mock_search_result = {
    "meta": {"total": 2, "pageCount": 1, "page": 1, "size": 10},
    "users": [
        {"firstName": "Bob", "lastName": "Johnson", "idpUsername": "BOBJOHNSON", "idpUserGuid": "FAKEID002", "idpType": "BCEID", "roles": [{"applicationName": "FOM_DEV", "roleName": "FOM_SUBMITTER", "roleDisplayName": "Submitter", "scopeType": "FOREST_CLIENT", "value": ["00001011", "00001012"]}]},
        {"firstName": "David", "lastName": "Brown", "idpUsername": "DAVIDB", "idpUserGuid": "FAKEID004", "idpType": "IDIR", "roles": [{"applicationName": "FOM_DEV", "roleName": "FOM_VIEWER", "roleDisplayName": "Viewer", "scopeType": None, "value": []}]}
    ]
}

# reusable method to patch the dependencies for user_search tests
@contextmanager
def patched_user_search_service(mock_app):
    with patch.object(crud_application, "get_application_by_app_client_id", return_value=mock_app), \
         patch.object(crud_utils, "allow_ext_call_api_permission", return_value=True), \
         patch("api.app.crud.services.ext_app_user_search_service.ExtAppUserSearchService") as MockService:
        yield MockService

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

    # test when requester does not have permission (no permitted role) to access the API
    with patch.object(crud_application, "get_application_by_app_client_id", return_value=mock_app), \
        patch.object(crud_utils, "allow_ext_call_api_permission", return_value=False):
        response = test_client_fixture.get(f"{endPoint}", headers=auth_headers)
        jwt_utils.assert_error_response(response, FORBIDDEN, ERROR_PERMISSION_REQUIRED)
        assert "No permission to call" in response.json()["detail"]["description"]

def test_user_search_return_result(
    test_client_fixture: TestClient,
    auth_headers,
    override_depends__get_current_requester
):
    # test when no result found
    override_depends__get_current_requester()
    with patched_user_search_service(mock_app) as MockService:

        mock_service_instance = MockService.return_value
        mock_service_instance.search_users.return_value = mock_search_empty_result

        response = test_client_fixture.get(f"{endPoint}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_search_empty_result

    # test with simple result found
    with patch.object(crud_application, "get_application_by_app_client_id", return_value=mock_app), \
        patch.object(crud_utils, "allow_ext_call_api_permission", return_value=True), \
        patch("api.app.crud.services.ext_app_user_search_service.ExtAppUserSearchService") as MockService:
        mock_service_instance = MockService.return_value
        mock_service_instance.search_users.return_value = mock_search_result

        response = test_client_fixture.get(f"{endPoint}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_search_result


# ----------- Tests for page_params parameter schema validation ----------- #

def test_user_search_query_params(
    test_client_fixture: TestClient,
    auth_headers,
    override_depends__get_current_requester,
):
    override_depends__get_current_requester()
    captured_args = {} # to capture the args passed to search_users service method

    # mock method for ExtAppUserSearchService.search_users
    def capture_args(page_params, filter_params):
        captured_args['page'] = page_params.page
        captured_args['size'] = page_params.size
        return {"meta": {"total": 0,"pageCount": 0, "page": 1, "size": 50}, "users": []} # dummy, not important.

    with patched_user_search_service(mock_app) as MockService:
        mock_service_instance = MockService.return_value
        mock_service_instance.search_users.side_effect = capture_args

        # Valid: no params (defaults)
        response = test_client_fixture.get(endPoint, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert captured_args['page'] == EXT_MIN_PAGE
        assert captured_args['size'] == EXT_DEFAULT_PAGE_SIZE

        # Valid: custom params
        response = test_client_fixture.get(endPoint, headers=auth_headers, params={"page": 2, "size": 20})
        assert response.status_code == status.HTTP_200_OK
        assert captured_args['page'] == 2
        assert captured_args['size'] == 20

    # Invalid scenarios (should return 422)
    invalid_page_params_list = [
        {"size": 9},
        {"size": 101},
        {"size": 20.5},
        {"size": "xyz"},
        {"page": -1},
        {"page": 1.5},
        {"page": "abc"},
    ]
    for invalid_params in invalid_page_params_list:
        with patched_user_search_service(mock_app) as MockService:
            mock_service_instance = MockService.return_value
            mock_service_instance.search_users.side_effect = capture_args
            response = test_client_fixture.get(endPoint, headers=auth_headers, params=invalid_params)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "detail" in response.json()

# ----------- Tests for filter_params parameter schema validation ----------- #

def test_user_search_filter_params_schema_validation(
    test_client_fixture: TestClient,
    auth_headers,
    override_depends__get_current_requester,
):
    override_depends__get_current_requester()
    captured_args = {}

    def capture_args(page_params, filter_params):
        captured_args.update(filter_params.dict())
        return {"meta": {"total": 0,"pageCount": 0, "page": 1, "size": 10}, "users": []}

    with patched_user_search_service(mock_app) as MockService:
        mock_service_instance = MockService.return_value
        mock_service_instance.search_users.side_effect = capture_args

        # Valid: all fields
        params = {
            "idpType": "IDIR",
            "idpUsername": "bobuser",
            "firstName": "Bob",
            "lastName": "Johnson",
            "role": "FOM_SUBMITTER"
        }
        response = test_client_fixture.get(endPoint, headers=auth_headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        assert captured_args["idp_type"] == "IDIR"
        assert captured_args["idp_username"] == "bobuser"
        assert captured_args["first_name"] == "Bob"
        assert captured_args["last_name"] == "Johnson"
        assert captured_args["role"] == ["FOM_SUBMITTER"]

        # Valid: single role
        params = {"role": "FOM_SUBMITTER"}
        response = test_client_fixture.get(endPoint, headers=auth_headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        assert captured_args["role"] == ["FOM_SUBMITTER"]

        # Valid: no filter params
        response = test_client_fixture.get(endPoint, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    # Invalid scenarios (should return 422)
    invalid_filter_params_list = [
        {"idpType": "INVALID"},  # not in allowed values
        {"idpType": "BCEIDEXTRA"},  # too long
        {"idpUsername": "a" * 21},  # too long
        {"firstName": "a" * 51},  # too long
        {"lastName": "a" * 51},  # too long
        {"role": "AAAAAAAAAAAAAAAAAAAAAAAAAA"},  # role name too long
        {"role": ",".join([f"ROLE{i}" for i in range(6)])},  # too many roles
    ]
    for invalid_params in invalid_filter_params_list:
        with patched_user_search_service(mock_app) as MockService:
            mock_service_instance = MockService.return_value
            mock_service_instance.search_users.side_effect = capture_args
            response = test_client_fixture.get(endPoint, headers=auth_headers, params=invalid_params)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
