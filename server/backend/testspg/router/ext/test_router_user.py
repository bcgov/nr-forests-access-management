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
from requests import HTTPError
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
        {"role": [f"ROLE{i}" for i in range(6)]},  # too many roles, multiple roles: send as list for query param
    ]
    for invalid_params in invalid_filter_params_list:
        with patched_user_search_service(mock_app) as MockService:
            mock_service_instance = MockService.return_value
            mock_service_instance.search_users.side_effect = capture_args
            response = test_client_fixture.get(endPoint, headers=auth_headers, params=invalid_params)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY



# ========== Tests for search_idir_users endpoint (/identity/idir/search) ========== #

searchIdirUsersEndpoint = f"{external_v1_api_prefix}/users/identity/idir/search"

# Mock IDIM proxy responses
mock_idir_empty_result = {
    "totalItems": 0,
    "pageSize": 10,
    "items": []
}

mock_idir_single_result = {
    "totalItems": 1,
    "pageSize": 10,
    "items": [
        {
            "userId": "CMENG",
            "guid": "00000001000000000000001",
            "firstName": "Chen",
            "lastName": "Meng",
            "email": "chen.meng@gov.bc.ca"
        }
    ]
}

mock_idir_multiple_results = {
    "totalItems": 2,
    "pageSize": 10,
    "items": [
        {
            "userId": "CMENG",
            "guid": "00000001000000000000001",
            "firstName": "Chen",
            "lastName": "Meng",
            "email": "chen.meng@gov.bc.ca"
        },
        {
            "userId": "JSMITH",
            "guid": "00000002000000000000002",
            "firstName": "John",
            "lastName": "Smith",
            "email": "john.smith@gov.bc.ca"
        }
    ]
}

# Helper context manager to patch search_idir_users service and auth
@contextmanager
def patched_search_idir_users(mock_app, mock_idim_response=None):
    if mock_idim_response is None:
        mock_idim_response = mock_idir_empty_result

    with patch.object(crud_application, "get_application_by_app_client_id", return_value=mock_app), \
         patch.object(crud_utils, "allow_ext_call_api_permission", return_value=True), \
         patch("api.app.routers.ext.router_user.IdimProxyService") as MockIdimServiceClass:
        # Configure the mock to return mock_idim_response when search_idir_users is called
        mock_instance = MagicMock()
        mock_instance.search_idir_users.return_value = mock_idim_response
        MockIdimServiceClass.return_value = mock_instance
        yield MockIdimServiceClass


class TestSearchIdirUsers:
    """
    Grouped tests for the /identity/idir/search endpoint.
    """

    def test_bearer_token_required(self, test_client_fixture: TestClient, test_rsa_key):
        """Test that bearer token is required for search_idir_users endpoint."""
        # No token - without search params, validation happens first and returns 422
        response = test_client_fixture.get(searchIdirUsersEndpoint)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # No token with search params - now auth check happens first
        response = test_client_fixture.get(searchIdirUsersEndpoint, params={"firstName": "Test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Expired token with search params
        claims = jwt_utils.create_jwt_claims()
        claims['exp'] = time.time() - 100000
        token = jwt_utils.create_jwt_token(test_rsa_key, claims=claims)
        response = test_client_fixture.get(searchIdirUsersEndpoint, headers=jwt_utils.headers(token), params={"firstName": "Test"})
        jwt_utils.assert_error_response(response, 401, ERROR_EXPIRED_TOKEN)

    def test_authorization_guard(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test that search_idir_users enforces authorize_ext_api_by_app_role guard."""
        override_depends__get_current_requester()

        # Case 1: Application not found
        with patch.object(crud_application, "get_application_by_app_client_id", return_value=None):
            response = test_client_fixture.get(searchIdirUsersEndpoint, headers=auth_headers, params={"firstName": "Test"})
            jwt_utils.assert_error_response(response, FORBIDDEN, ERROR_CODE_INVALID_OPERATION)

        # Case 2: Requester has no permission
        with patch.object(crud_application, "get_application_by_app_client_id", return_value=mock_app), \
             patch.object(crud_utils, "allow_ext_call_api_permission", return_value=False):
            response = test_client_fixture.get(searchIdirUsersEndpoint, headers=auth_headers, params={"firstName": "Test"})
            jwt_utils.assert_error_response(response, FORBIDDEN, ERROR_PERMISSION_REQUIRED)
            assert "No permission to call" in response.json()["detail"]["description"]

    def test_by_first_name_single_result(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test successful search by firstName field, returning single result."""
        override_depends__get_current_requester()

        with patched_search_idir_users(mock_app, mock_idir_single_result):
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={"firstName": "Chen"}
            )

            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["totalItems"] == 1
            assert result["pageSize"] == 10
            assert len(result["items"]) == 1
            assert result["items"][0]["userId"] == "CMENG"
            assert result["items"][0]["firstName"] == "Chen"

    def test_by_last_name_multiple_results(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test successful search by lastName field, returning multiple results."""
        override_depends__get_current_requester()

        with patched_search_idir_users(mock_app, mock_idir_multiple_results):
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={"lastName": "en"}  # matches "Meng" and "Smith" with partial match, minimum 2 chars required
            )

            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["totalItems"] == 2
            assert len(result["items"]) == 2

    def test_by_user_id(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test successful search by userId field."""
        override_depends__get_current_requester()

        with patched_search_idir_users(mock_app, mock_idir_single_result):
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={"userId": "CMENG"}
            )

            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["totalItems"] == 1
            assert result["items"][0]["userId"] == "CMENG"

    def test_by_combined_fields(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test search with multiple fields (firstName and lastName)."""
        override_depends__get_current_requester()

        with patched_search_idir_users(mock_app, mock_idir_single_result):
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={"firstName": "Chen", "lastName": "Meng"}
            )

            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["totalItems"] == 1

    def test_no_results(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test search that returns empty result set."""
        override_depends__get_current_requester()

        with patched_search_idir_users(mock_app, mock_idir_empty_result):
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={"firstName": "NonExistent"}
            )

            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["totalItems"] == 0
            assert len(result["items"]) == 0

    def test_validation_no_field_provided(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test validation failure when no search field is provided."""
        override_depends__get_current_requester()

        response = test_client_fixture.get(
            searchIdirUsersEndpoint,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_field_too_short(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test validation failure when provided field has fewer than 2 characters."""
        override_depends__get_current_requester()

        invalid_params_list = [
            {"firstName": "A"},       # 1 char
            {"lastName": "B"},        # 1 char
            {"userId": "X"},          # 1 char
            {"firstName": "A", "lastName": "Test"},  # firstName too short
        ]

        for params in invalid_params_list:
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params=params
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_match_mode_user_provided(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test that user-provided match modes are passed to IDIM service."""
        override_depends__get_current_requester()

        with patched_search_idir_users(mock_app, mock_idir_single_result):
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={
                    "firstName": "Chen",
                    "firstNameMatchMode": "StartsWith",
                    "lastNameMatchMode": "Exact"
                }
            )

            assert response.status_code == status.HTTP_200_OK

    def test_match_mode_defaults_to_contains(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test that match modes default to 'Contains' when not explicitly provided."""
        override_depends__get_current_requester()

        with patched_search_idir_users(mock_app, mock_idir_multiple_results):
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={"firstName": "Chen", "lastName": "Meng"}
                # No explicit match modes provided
            )

            assert response.status_code == status.HTTP_200_OK

    def test_idim_proxy_error_with_code(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test error handling when IDIM Proxy returns error."""
        override_depends__get_current_requester()

        with patch.object(crud_application, "get_application_by_app_client_id", return_value=mock_app), \
             patch.object(crud_utils, "allow_ext_call_api_permission", return_value=True), \
             patch("api.app.routers.ext.router_user.IdimProxyService") as MockIdimServiceClass:

            mock_instance = MagicMock()
            # Simulate a real IDIM Proxy 400 response payload.
            idim_error_payload = {
                "message": [
                    "requesterUserGuid must be longer than or equal to 32 characters"
                ],
                "error": "Bad Request",
                "statusCode": 400,
            }
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_400_BAD_REQUEST
            mock_response.reason = "Bad Request"
            mock_response.text = (
                '{"message": ["requesterUserGuid must be longer than or equal to '
                '32 characters"], "error": "Bad Request", "statusCode": 400}'
            )
            mock_instance.search_idir_users.side_effect = HTTPError(response=mock_response)
            MockIdimServiceClass.return_value = mock_instance

            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={"firstName": "Chen"}
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {
                "failureCode": None,
                "message": idim_error_payload["message"],
            }

    def test_page_size_parameter(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test that pageSize parameter is correctly passed through."""
        override_depends__get_current_requester()

        with patched_search_idir_users(mock_app, mock_idir_single_result):
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={"firstName": "Chen", "pageSize": 25}
            )

            assert response.status_code == status.HTTP_200_OK

    def test_input_trimming(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test that input fields are trimmed before validation."""
        override_depends__get_current_requester()

        with patched_search_idir_users(mock_app, mock_idir_single_result):
            # Input with leading/trailing whitespace
            response = test_client_fixture.get(
                searchIdirUsersEndpoint,
                headers=auth_headers,
                params={"firstName": "  Chen  ", "lastName": "  Meng  "}
            )

            assert response.status_code == status.HTTP_200_OK

    def test_whitespace_only_field_becomes_none(self, test_client_fixture: TestClient, auth_headers, override_depends__get_current_requester):
        """Test that fields containing only whitespace are treated as None."""
        override_depends__get_current_requester()

        # This should fail validation because after trimming, no field is provided
        response = test_client_fixture.get(
            searchIdirUsersEndpoint,
            headers=auth_headers,
            params={"firstName": "   ", "lastName": "\t\n"}  # Only whitespace
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        assert any("At least one of firstName, lastName, or userId must be provided" in str(err) for err in error_detail)
