import logging
from http import HTTPStatus
from fastapi.testclient import TestClient

from api.app.main import apiPrefix
from api.app.constants import ERROR_CODE_REQUESTER_NOT_EXISTS
from api.app.routers.router_guards import get_current_requester
from api.app.schemas import RequesterSchema
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED, ERROR_GROUPS_REQUIRED
from api.app.utils.utils import raise_http_exception
import testspg.jwt_utils as jwt_utils
from testspg.conftest import test_client_fixture
from testspg.constants import (
    TEST_IDIR_REQUESTER_DICT,
    TEST_BCEID_REQUESTER_DICT,
    TEST_VALID_BUSINESS_BCEID_USERNAME_ONE,
    TEST_VALID_BUSINESS_BCEID_USERNAME_TWO,
    FOM_DEV_APPLICATION_ID,
)


LOGGER = logging.getLogger(__name__)


endPoint_search_idir = f"{apiPrefix}/identity_search/idir"
endPoint_search_bceid = f"{apiPrefix}/identity_search/bceid"
endPoint_search_param_application_id = f"&application_id={FOM_DEV_APPLICATION_ID}"
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
def test_search_idir_with_valid_user_found_result(
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
        endPoint_search_idir
        + f"?user_id={valid_user_id_param}"
        + endPoint_search_param_application_id
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


def test_search_idir_with_invalid_user_return_not_found(
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
        endPoint_search_idir
        + f"?user_id={invalid_user_id_param}"
        + endPoint_search_param_application_id
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


def test_none_idir_user_cannot_search_idir_user(
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
        endPoint_search_idir
        + f"?user_id={valid_user_id_param}"
        + endPoint_search_param_application_id
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Action is not allowed for external user." in response.text


def test_search_idir_user_requester_not_found_error_raised(
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
        endPoint_search_idir
        + f"?user_id={valid_user_id_param}"
        + endPoint_search_param_application_id
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Requester does not exist" in response.text


# --------------------- Test search for Business BCEID --------------------------- #
def test_search_bceid_with_valid_user_same_org_found_result(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test business bceid user search valid business bceid user_id within same organization
    """
    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_business_bceid_user
    )
    test_end_point = (
        endPoint_search_bceid
        + f"?user_id={TEST_VALID_BUSINESS_BCEID_USERNAME_ONE}"
        + endPoint_search_param_application_id
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


def test_search_bceid_with_valid_user_diff_org_fail(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test business bceid user search valid business bceid user_id from different organization
    """
    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_business_bceid_user
    )
    test_end_point = (
        endPoint_search_bceid
        + f"?user_id={TEST_VALID_BUSINESS_BCEID_USERNAME_TWO}"
        + endPoint_search_param_application_id
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1


def test_search_bceid_with_valid_user_without_authorization_fail(
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
        endPoint_search_bceid
        + f"?user_id={TEST_VALID_BUSINESS_BCEID_USERNAME_ONE}"
        + endPoint_search_param_application_id
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key, [])
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_GROUPS_REQUIRED) != -1


def test_search_bceid_with_invalid_user_return_not_found(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test idir user search invalid business bceid user_id.
    """
    # override dependency for Requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_business_bceid_user
    )

    invalid_user_id_param = "USERNOTEXISTS"
    test_end_point = (
        endPoint_search_bceid
        + f"?user_id={invalid_user_id_param}"
        + endPoint_search_param_application_id
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["found"] == False
    assert response.json()["userId"] == invalid_user_id_param


def test_search_bceid_user_requester_not_found_error_raised(
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
        endPoint_search_bceid
        + f"?user_id={TEST_VALID_BUSINESS_BCEID_USERNAME_ONE}"
        + endPoint_search_param_application_id
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Requester does not exist" in response.text
