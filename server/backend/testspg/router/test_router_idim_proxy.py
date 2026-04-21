import logging
from contextlib import contextmanager
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import testspg.jwt_utils as jwt_utils
from api.app.constants import ERROR_CODE_REQUESTER_NOT_EXISTS
from api.app.jwt_validation import (ERROR_GROUPS_REQUIRED,
                                    ERROR_PERMISSION_REQUIRED)
from api.app.main import internal_api_prefix
from api.app.routers.router_guards import get_current_requester
from api.app.schemas import RequesterSchema
from api.app.utils.utils import raise_http_exception
from fastapi import status
from fastapi.testclient import TestClient
from requests import HTTPError
from testspg.conftest import test_client_fixture
from testspg.constants import (FOM_DEV_APPLICATION_ID,
                               TEST_BCEID_REQUESTER_DICT,
                               TEST_IDIR_REQUESTER_DICT,
                               TEST_VALID_BUSINESS_BCEID_USERNAME_ONE,
                               TEST_VALID_BUSINESS_BCEID_USERNAME_TWO)

LOGGER = logging.getLogger(__name__)


endPoint_lookup_idir = f"{internal_api_prefix}/identity-lookup/idir"
endPoint_lookup_bceid = f"{internal_api_prefix}/identity-lookup/bceid"
endPoint_lookup_param_application_id = f"&application_id={FOM_DEV_APPLICATION_ID}"
valid_user_id_param = "CMENG"
valid_user_id_param_business_bceid = "LOAD-2-TEST"


async def mock_get_current_requester_with_idir_user():
    """
    A mock for router dependency, for Requester who is IDIR user.
    """
    return RequesterSchema(**TEST_IDIR_REQUESTER_DICT)


async def mock_get_current_requester_with_business_bceid_user():
    """
    A mock for router dependency, for Requester who is not IDIR user.
    """
    return RequesterSchema(**TEST_BCEID_REQUESTER_DICT)


async def mock_get_current_requester_user_not_exists():
    """
    A mock for router dependency, for Requester who does not exists.
    """
    raise_http_exception(
        status_code=HTTPStatus.FORBIDDEN,
        error_code=ERROR_CODE_REQUESTER_NOT_EXISTS,
        error_msg="Requester does not exist, action is not allowed.",
    )


# -------------------- Test search for IDIR ---------------------------- #
@pytest.mark.skip(
    reason="Temporary IDIR search production fix break this test. Fix or enable later."
)
def test_lookup_idir_with_valid_user_found_result(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test valid user_id to search.
    """
    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_idir_user
    )

    test_end_point = (
        endPoint_lookup_idir
        + f"?user_id={valid_user_id_param}"
        + endPoint_lookup_param_application_id
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["found"] == True
    assert response.json()["userId"] == valid_user_id_param
    assert response.json()["firstName"] is not None
    assert response.json()["lastName"] is not None


@pytest.mark.skip(
    reason="Temporary IDIR search production fix break this test. Fix or enable later."
)
def test_lookup_idir_with_invalid_user_return_not_found(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test invalid user_id to search.
    """
    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_idir_user
    )

    invalid_user_id_param = "USERNOTEXISTS"
    test_end_point = (
        endPoint_lookup_idir
        + f"?user_id={invalid_user_id_param}"
        + endPoint_lookup_param_application_id
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["found"] == False
    assert response.json()["userId"] == invalid_user_id_param
    assert response.json()["firstName"] is None
    assert response.json()["lastName"] is None


def test_none_idir_user_cannot_lookup_idir_user(
    test_client_fixture: TestClient, test_rsa_key
):
    """
    Test Requester is external.
    """

    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_business_bceid_user
    )

    test_end_point = (
        endPoint_lookup_idir
        + f"?user_id={valid_user_id_param}"
        + endPoint_lookup_param_application_id
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Action is not allowed for external user." in response.text


def test_lookup_idir_user_requester_not_found_error_raised(
    test_client_fixture: TestClient, test_rsa_key
):
    """
    Test Requester does not exist.
    """

    # override dependency for Requester not exists.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_user_not_exists
    )

    test_end_point = (
        endPoint_lookup_idir
        + f"?user_id={valid_user_id_param}"
        + endPoint_lookup_param_application_id
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Requester does not exist" in response.text


# --------------------- Test lookup for Business BCEID --------------------------- #
def test_lookup_business_bceid_with_valid_user_same_org_found_result(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test business bceid user lookup valid business bceid user_id within same organization
    """
    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_business_bceid_user
    )
    test_end_point = (
        endPoint_lookup_bceid
        + f"?user_id={TEST_VALID_BUSINESS_BCEID_USERNAME_ONE}"
        + endPoint_lookup_param_application_id
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["found"] == True
    assert response.json()["userId"] == TEST_VALID_BUSINESS_BCEID_USERNAME_ONE
    assert response.json()["guid"] is not None
    assert response.json()["businessGuid"] is not None
    assert response.json()["businessLegalName"] is not None
    assert response.json()["firstName"] is not None
    assert response.json()["lastName"] is not None


def test_lookup_business_bceid_with_valid_user_diff_org_fail(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test business bceid user lookup valid business bceid user_id from different organization
    """
    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_business_bceid_user
    )
    test_end_point = (
        endPoint_lookup_bceid
        + f"?user_id={TEST_VALID_BUSINESS_BCEID_USERNAME_TWO}"
        + endPoint_lookup_param_application_id
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1


def test_lookup_business_bceid_with_valid_user_without_authorization_fail(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test business bceid user search valid business bceid user_id without authorization
    """
    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_business_bceid_user
    )
    test_end_point = (
        endPoint_lookup_bceid
        + f"?user_id={TEST_VALID_BUSINESS_BCEID_USERNAME_ONE}"
        + endPoint_lookup_param_application_id
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key, [])
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_GROUPS_REQUIRED) != -1


def test_lookup_business_bceid_with_invalid_user_return_not_found(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test idir user lookup invalid business bceid user_id.
    """
    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_business_bceid_user
    )

    invalid_user_id_param = "USERNOTEXISTS"
    test_end_point = (
        endPoint_lookup_bceid
        + f"?user_id={invalid_user_id_param}"
        + endPoint_lookup_param_application_id
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["found"] == False
    assert response.json()["userId"] == invalid_user_id_param


def test_lookup_bceid_user_requester_not_found_error_raised(
    test_client_fixture: TestClient, test_rsa_key
):
    """
    Test Requester does not exist.
    """

    # override dependency for Requester not exists.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_user_not_exists
    )

    test_end_point = (
        endPoint_lookup_bceid
        + f"?user_id={TEST_VALID_BUSINESS_BCEID_USERNAME_ONE}"
        + endPoint_lookup_param_application_id
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Requester does not exist" in response.text


def test_lookup_idir_user_id_too_long_returns_422(
    test_client_fixture: TestClient, test_rsa_key
):
    """
    Ensure that passing a user_id exceeding max_length=20 returns 422 (not 500).
    Validates that Annotated[str, Query(max_length=20)] is handled correctly
    by FastAPI's validation layer.
    """
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_idir_user
    )

    token = jwt_utils.create_jwt_token(test_rsa_key)
    too_long_user_id = "A" * 21  # exceeds max_length=20
    test_end_point = (
        endPoint_lookup_idir
        + f"?user_id={too_long_user_id}"
        + endPoint_lookup_param_application_id
    )
    response = test_client_fixture.get(
        test_end_point, headers=jwt_utils.headers(token)
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_lookup_bceid_user_id_too_long_returns_422(
    test_client_fixture: TestClient, test_rsa_key
):
    """
    Ensure that passing a user_id exceeding max_length=20 returns 422 (not 500).
    Validates that Annotated[str, Query(max_length=20)] is handled correctly
    by FastAPI's validation layer.
    """
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_business_bceid_user
    )

    token = jwt_utils.create_jwt_token(test_rsa_key)
    too_long_user_id = "A" * 21  # exceeds max_length=20
    test_end_point = (
        endPoint_lookup_bceid
        + f"?user_id={too_long_user_id}"
        + endPoint_lookup_param_application_id
    )
    response = test_client_fixture.get(
        test_end_point, headers=jwt_utils.headers(token)
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# --------------------- IDIR users search tests --------------------------- #
idir_search_users_endpoint = (
    f"{internal_api_prefix}/identity-lookup/users/idir/search"
)

class TestIdirSearchUsers:
    """
    Test class for IDIR users search endpoint.
    """

    @staticmethod
    def _search_endpoint_with_app_id():
        return idir_search_users_endpoint

    @staticmethod
    def _with_app_id(params=None):
        merged = {"application_id": FOM_DEV_APPLICATION_ID}
        if params:
            merged.update(params)
        return merged

    @staticmethod
    @contextmanager
    def _patch_idim_service(search_result=None, side_effect=None):
        if search_result is None:
            search_result = {
                "totalItems": 0,
                "pageSize": 10,
                "items": [],
            }

        with patch("api.app.routers.router_idim_proxy.IdimProxyService") as mock_service_cls:
            mock_instance = MagicMock()
            mock_instance.search_idir_users.return_value = search_result
            if side_effect is not None:
                mock_instance.search_idir_users.side_effect = side_effect
            mock_service_cls.return_value = mock_instance
            yield mock_instance

    def test_bearer_token_required(self, test_client_fixture: TestClient, test_rsa_key):
        app = test_client_fixture.app
        app.dependency_overrides[get_current_requester] = (
            mock_get_current_requester_with_idir_user
        )

        endpoint = self._search_endpoint_with_app_id()

        response = test_client_fixture.get(
            endpoint,
            params=self._with_app_id({"firstName": "Chen"}),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        claims = jwt_utils.create_jwt_claims()
        claims["exp"] = 1
        expired_token = jwt_utils.create_jwt_token(test_rsa_key, claims=claims)
        response = test_client_fixture.get(
            endpoint,
            headers=jwt_utils.headers(expired_token),
            params=self._with_app_id({"firstName": "Chen"}),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_success_returns_single_result(
        self, test_client_fixture: TestClient, test_rsa_key
    ):
        app = test_client_fixture.app
        app.dependency_overrides[get_current_requester] = (
            mock_get_current_requester_with_idir_user
        )

        token = jwt_utils.create_jwt_token(test_rsa_key)
        endpoint = self._search_endpoint_with_app_id()
        expected = {
            "totalItems": 1,
            "pageSize": 10,
            "items": [
                {
                    "userId": "CMENG",
                    "guid": "00000001000000000000001",
                    "firstName": "Chen",
                    "lastName": "Meng",
                    "email": "c.me@gov.bc.ca",
                }
            ],
        }

        with self._patch_idim_service(search_result=expected):
            response = test_client_fixture.get(
                endpoint,
                headers=jwt_utils.headers(token),
                params=self._with_app_id({"firstName": "Chen"}),
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    def test_success_returns_empty_result(
        self, test_client_fixture: TestClient, test_rsa_key
    ):
        app = test_client_fixture.app
        app.dependency_overrides[get_current_requester] = (
            mock_get_current_requester_with_idir_user
        )

        token = jwt_utils.create_jwt_token(test_rsa_key)
        endpoint = self._search_endpoint_with_app_id()

        with self._patch_idim_service(search_result={"totalItems": 0, "pageSize": 10, "items": []}):
            response = test_client_fixture.get(
                endpoint,
                headers=jwt_utils.headers(token),
                params=self._with_app_id({"firstName": "NotExists"}),
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["totalItems"] == 0
        assert response.json()["items"] == []

    def test_validation_no_search_field(
        self, test_client_fixture: TestClient, test_rsa_key
    ):
        app = test_client_fixture.app
        app.dependency_overrides[get_current_requester] = (
            mock_get_current_requester_with_idir_user
        )

        token = jwt_utils.create_jwt_token(test_rsa_key)
        endpoint = self._search_endpoint_with_app_id()

        response = test_client_fixture.get(
            endpoint,
            headers=jwt_utils.headers(token),
            params=self._with_app_id(),
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_search_field_too_short(
        self, test_client_fixture: TestClient, test_rsa_key
    ):
        app = test_client_fixture.app
        app.dependency_overrides[get_current_requester] = (
            mock_get_current_requester_with_idir_user
        )

        token = jwt_utils.create_jwt_token(test_rsa_key)
        endpoint = self._search_endpoint_with_app_id()

        invalid_params_list = [
            {"firstName": "A"},
            {"lastName": "B"},
            {"userId": "X"},
            {"firstName": "A", "lastName": "Test"},
        ]

        for invalid_params in invalid_params_list:
            response = test_client_fixture.get(
                endpoint,
                headers=jwt_utils.headers(token),
                params=self._with_app_id(invalid_params),
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_ignores_public_match_mode_params(
        self, test_client_fixture: TestClient, test_rsa_key
    ):
        app = test_client_fixture.app
        app.dependency_overrides[get_current_requester] = (
            mock_get_current_requester_with_idir_user
        )

        token = jwt_utils.create_jwt_token(test_rsa_key)
        endpoint = self._search_endpoint_with_app_id()

        with self._patch_idim_service(search_result={"totalItems": 0, "pageSize": 10, "items": []}) as mock_instance:
            response = test_client_fixture.get(
                endpoint,
                headers=jwt_utils.headers(token),
                params=self._with_app_id({
                    "firstName": "Chen",
                    "firstNameMatchMode": "StartsWith",
                    "lastName": "Meng",
                    "lastNameMatchMode": "Exact",
                }),
            )

        assert response.status_code == status.HTTP_200_OK
        called_search_params = mock_instance.search_idir_users.call_args[0][0]
        assert called_search_params.to_query_params()["firstNameMatchMode"] == "Contains"
        assert called_search_params.to_query_params()["lastNameMatchMode"] == "Contains"

    def test_search_always_uses_contains_match_mode(
        self, test_client_fixture: TestClient, test_rsa_key
    ):
        app = test_client_fixture.app
        app.dependency_overrides[get_current_requester] = (
            mock_get_current_requester_with_idir_user
        )

        token = jwt_utils.create_jwt_token(test_rsa_key)
        endpoint = self._search_endpoint_with_app_id()

        with self._patch_idim_service(search_result={"totalItems": 0, "pageSize": 10, "items": []}) as mock_instance:
            response = test_client_fixture.get(
                endpoint,
                headers=jwt_utils.headers(token),
                params=self._with_app_id({"firstName": "Chen", "lastName": "Meng"}),
            )

        assert response.status_code == status.HTTP_200_OK
        called_search_params = mock_instance.search_idir_users.call_args[0][0]
        assert called_search_params.to_query_params()["firstNameMatchMode"] == "Contains"
        assert called_search_params.to_query_params()["lastNameMatchMode"] == "Contains"

    def test_error_propagation_with_code(
        self, test_client_fixture: TestClient, test_rsa_key
    ):
        app = test_client_fixture.app
        app.dependency_overrides[get_current_requester] = (
            mock_get_current_requester_with_idir_user
        )

        token = jwt_utils.create_jwt_token(test_rsa_key)
        endpoint = self._search_endpoint_with_app_id()

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_400_BAD_REQUEST
        mock_response.reason = "Bad Request"
        mock_response.text = (
            '{"message": ["requesterUserGuid must be longer than or equal to 32 characters"], '
            '"error": "Bad Request", "statusCode": 400}'
        )

        with self._patch_idim_service(side_effect=HTTPError(response=mock_response)):
            response = test_client_fixture.get(
                endpoint,
                headers=jwt_utils.headers(token),
                params=self._with_app_id({"firstName": "Chen"}),
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "failureCode": None,
            "message": ["requesterUserGuid must be longer than or equal to 32 characters"],
        }

    def test_unauthorized_without_required_group(
        self, test_client_fixture: TestClient, test_rsa_key
    ):
        app = test_client_fixture.app
        app.dependency_overrides[get_current_requester] = (
            mock_get_current_requester_with_idir_user
        )

        token_without_roles = jwt_utils.create_jwt_token(test_rsa_key, roles=[])
        endpoint = self._search_endpoint_with_app_id()

        response = test_client_fixture.get(
            endpoint,
            headers=jwt_utils.headers(token_without_roles),
            params=self._with_app_id({"firstName": "Chen"}),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert ERROR_GROUPS_REQUIRED in str(response.json()["detail"])

