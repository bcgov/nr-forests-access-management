"""
Tests for service-account (client-credentials / machine-to-machine) token support
on the external (/external/v1) API.

A service-account token carries no user identity (no "username" claim). The external
endpoints accept it and authorize it by the token's client_id mapping to a registered
application client (FamApplicationClient). The per-user role / call_api_flag check is
bypassed for service accounts. The /me/role-metadata endpoint, which reports the
authenticated user's own roles, rejects service-account tokens with a 400.
"""
import logging
from http.client import BAD_REQUEST, FORBIDDEN
from unittest.mock import MagicMock, patch

import jwt
from api.app.constants import ERROR_CODE_INVALID_OPERATION
from api.app.crud import crud_application, crud_utils
from api.app.crud.services.ext_app_user_search_service import \
    ExtAppUserSearchService
from api.app.jwt_validation import is_service_account_token
from api.app.main import external_v1_api_prefix
from api.app.schemas.requester import RequesterSchema
from fastapi import status
from fastapi.testclient import TestClient
from testspg import jwt_utils

LOGGER = logging.getLogger(__name__)

usersEndpoint = f"{external_v1_api_prefix}/users"
idirSearchEndpoint = f"{external_v1_api_prefix}/users/identity/idir/search"
meEndpoint = f"{external_v1_api_prefix}/users/me/role-metadata"

mock_app = MagicMock()
mock_app.application_id = 123
mock_app.application_name = "FOM_DEV"

mock_search_empty_result = {
    "meta": {"total": 0, "pageCount": 0, "page": 1, "size": 10},
    "users": [],
}
mock_idir_empty_result = {"totalItems": 0, "pageSize": 10, "items": []}


def service_account_headers(test_rsa_key):
    """Build a validly-signed access token with NO 'username' claim (service account)."""
    claims = jwt_utils.create_jwt_claims()
    del claims["username"]
    token = jwt.encode(
        claims, test_rsa_key, algorithm="RS256", headers={"kid": "12345"}
    )
    return jwt_utils.headers(token)


# --------------------------- unit-level behavior --------------------------- #

def test_is_service_account_token_detects_missing_username():
    user_claims = jwt_utils.create_jwt_claims()
    assert is_service_account_token(user_claims) is False

    service_claims = jwt_utils.create_jwt_claims()
    del service_claims["username"]
    assert is_service_account_token(service_claims) is True


def test_requester_schema_supports_service_account():
    requester = RequesterSchema(
        is_service_account=True, service_account_client_id="svc-client-123"
    )
    assert requester.is_service_account is True
    assert requester.user_name is None
    assert requester.user_id is None
    assert requester.user_guid is None
    assert "svc-client-123" in requester.log_identity()


def test_is_request_allowed_true_for_service_account_without_db():
    # is_request_allowed short-circuits for service accounts; no DB / user lookup.
    service_requester = RequesterSchema(
        is_service_account=True, service_account_client_id="svc-client-123"
    )
    service = ExtAppUserSearchService(
        db=None, requester=service_requester, application_id=mock_app.application_id
    )
    assert service.is_request_allowed() is True


# --------------------------- endpoint behavior --------------------------- #

def test_user_search_service_account_bypasses_user_permission(
    test_client_fixture: TestClient, test_rsa_key
):
    # Service account is authorized purely by app-client mapping. Even with the
    # per-user permission check returning False, the call succeeds (it is bypassed).
    with patch.object(
        crud_application, "get_application_by_app_client_id", return_value=mock_app
    ), patch.object(
        crud_utils, "allow_ext_call_api_permission", return_value=False
    ), patch(
        "api.app.crud.services.ext_app_user_search_service.ExtAppUserSearchService"
    ) as MockService:
        MockService.return_value.search_users.return_value = mock_search_empty_result

        response = test_client_fixture.get(
            usersEndpoint, headers=service_account_headers(test_rsa_key)
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_search_empty_result


def test_user_search_service_account_unregistered_client_forbidden(
    test_client_fixture: TestClient, test_rsa_key
):
    # client_id not mapped to any registered application -> 403.
    with patch.object(
        crud_application, "get_application_by_app_client_id", return_value=None
    ):
        response = test_client_fixture.get(
            usersEndpoint, headers=service_account_headers(test_rsa_key)
        )
        jwt_utils.assert_error_response(
            response, FORBIDDEN, ERROR_CODE_INVALID_OPERATION
        )


def test_idir_search_service_account_bypasses_user_permission(
    test_client_fixture: TestClient, test_rsa_key
):
    with patch.object(
        crud_application, "get_application_by_app_client_id", return_value=mock_app
    ), patch.object(
        crud_utils, "allow_ext_call_api_permission", return_value=False
    ), patch(
        "api.app.routers.ext.router_user.IdimProxyService"
    ) as MockIdimServiceClass:
        MockIdimServiceClass.return_value.search_idir_users.return_value = (
            mock_idir_empty_result
        )

        response = test_client_fixture.get(
            idirSearchEndpoint,
            headers=service_account_headers(test_rsa_key),
            params={"firstName": "Test"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_idir_empty_result


def test_me_role_metadata_rejects_service_account(
    test_client_fixture: TestClient, test_rsa_key
):
    # "me" has no meaning for a service account -> clean 400.
    response = test_client_fixture.get(
        meEndpoint, headers=service_account_headers(test_rsa_key)
    )
    jwt_utils.assert_error_response(
        response, BAD_REQUEST, ERROR_CODE_INVALID_OPERATION
    )
