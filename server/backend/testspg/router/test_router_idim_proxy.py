import logging
from http import HTTPStatus
import os
import pytest

import testspg.jwt_utils as jwt_utils
from api.app.constants import UserType
from api.app.main import apiPrefix
from api.app.routers.router_guards import get_current_requester, no_requester_exception
from api.app.schemas import Requester
from fastapi.testclient import TestClient
from testspg.conftest import test_client_fixture
from testspg.constants import TEST_IDIR_REQUESTER_DICT

LOGGER = logging.getLogger(__name__)

endPoint_search_idir = f"{apiPrefix}/identity_search/idir"
endPoint_search_bceid = f"{apiPrefix}/identity_search/bceid"
valid_user_id_param = "CMENG"
valid_user_id_param_business_bceid = "LOAD-2-TEST"


async def mock_get_current_requester_with_idir_user():
    """
    A mock for router dependency, for requester who is IDIR user.
    """
    return Requester(**TEST_IDIR_REQUESTER_DICT)


async def mock_get_current_requester_with_none_idir_user():
    """
    A mock for router dependency, for requester who is not IDIR user.
    """
    none_idir_requester = {**TEST_IDIR_REQUESTER_DICT}
    none_idir_requester["user_type_code"] = UserType.BCEID  # Set to none-IDIR
    return Requester(**none_idir_requester)


async def mock_get_current_requester_user_not_exists():
    """
    A mock for router dependency, for requester who does not exists.
    """
    raise no_requester_exception


def test_search_idir_with_valid_user_found_result(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test valid user_id to search.
    """
    # override dependency for requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_idir_user
    )

    test_end_point = endPoint_search_idir + f"?user_id={valid_user_id_param}"
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
    # override dependency for requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_idir_user
    )

    invalid_user_id_param = "USERNOTEXISTS"
    test_end_point = endPoint_search_idir + f"?user_id={invalid_user_id_param}"
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
    Test requester is external.
    """

    # override dependency for requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_none_idir_user
    )

    test_end_point = endPoint_search_idir + f"?user_id={valid_user_id_param}"
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
    Test requester does not exist.
    """

    # override dependency for requester not exists.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_user_not_exists
    )

    test_end_point = endPoint_search_idir + f"?user_id={valid_user_id_param}"
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Requester does not exist" in response.text


@pytest.mark.skip(
    reason="need idir user guid to run this test, switch to use bceid search bceid later"
)
def test_search_bceid_with_valid_user_found_result(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test idir user search valid business bceid user_id.
    """
    # override dependency for requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_idir_user
    )
    test_end_point = (
        endPoint_search_bceid + f"?user_id={valid_user_id_param_business_bceid}"
    )
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["found"] == True
    assert response.json()["userId"] == valid_user_id_param_business_bceid
    assert response.json()["guid"] is not None
    assert response.json()["businessGuid"] is not None
    assert response.json()["businessLegalName"] is not None
    assert response.json()["firstName"] is not None
    assert response.json()["lastName"] is not None


@pytest.mark.skip(
    reason="need idir user guid to run this test, switch to use bceid search bceid later"
)
def test_search_bceid_with_invalid_user_return_not_found(
    test_client_fixture: test_client_fixture, test_rsa_key
):
    """
    Test idir user search invalid business bceid user_id.
    """
    # override dependency for requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_with_idir_user
    )

    invalid_user_id_param = "USERNOTEXISTS"
    test_end_point = endPoint_search_bceid + f"?user_id={invalid_user_id_param}"
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
    Test requester does not exist.
    """

    # override dependency for requester not exists.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = (
        mock_get_current_requester_user_not_exists
    )

    test_end_point = (
        endPoint_search_bceid + f"?user_id={valid_user_id_param_business_bceid}"
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Requester does not exist" in response.text
