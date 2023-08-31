import logging
from http import HTTPStatus

import testspg.jwt_utils as jwt_utils
from api.app import jwt_validation
from api.app.constants import UserType
from api.app.main import apiPrefix
from api.app.routers.router_guards import (get_current_requester,
                                           no_requester_exception)
from api.app.schemas import Requester
from api.app.utils.utils import read_json_file
from fastapi.testclient import TestClient
from testspg.conftest import test_client_fixture

LOGGER = logging.getLogger(__name__)

endPoint_search = f"{apiPrefix}/identity_search/idir"
valid_user_id_param = "CMENG"

# Override this.
# Valid sample IDIR type ("user_type": "I") requester
sample_idir_requester_dict = {
    "cognito_user_id": "dev-idir_e72a12c916a44f39e5dcdffae7@idir",
    "user_name": "IANLIU",
    "user_type": "I",
    "access_roles": ["FAM_ACCESS_ADMIN", "FOM_DEV_ACCESS_ADMIN"]
}

async def mock_get_current_requester_with_idir_user():
    """
    A mock for router dependency, for requester who is IDIR user.
    """
    return Requester(**sample_idir_requester_dict)

async def mock_get_current_requester_with_none_idir_user():
    """
    A mock for router dependency, for requester who is not IDIR user.
    """
    none_idir_requester = sample_idir_requester_dict
    none_idir_requester["user_type"] = UserType.BCEID # Set to none-IDIR
    return Requester(**none_idir_requester)

async def mock_get_current_requester_user_not_exists():
    """
    A mock for router dependency, for requester who does not exists.
    """
    raise no_requester_exception


def test_search_idir_with_valid_user_found_result(
    test_client_fixture: test_client_fixture,
    test_rsa_key
):
    """
    Test valid user_id to search.
    """
    # override dependency for requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = mock_get_current_requester_with_idir_user

    test_end_point = endPoint_search + f"?user_id={valid_user_id_param}"
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(f"{test_end_point}", headers=jwt_utils.headers(token))

    assert response.status_code == HTTPStatus.OK
    assert response.json()['found'] == True
    assert response.json()['userId'] == valid_user_id_param

def test_search_idir_with_invalid_user_return_not_found(
    test_client_fixture: test_client_fixture,
    test_rsa_key
):
    """
    Test invalid user_id to search.
    """
    # override dependency for requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = mock_get_current_requester_with_idir_user

    invalid_user_id_param = "USERNOTEXISTS"
    test_end_point = endPoint_search + f"?user_id={invalid_user_id_param}"
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(f"{test_end_point}", headers=jwt_utils.headers(token))

    assert response.status_code == HTTPStatus.OK
    assert response.json()['found'] == False
    assert response.json()['userId'] == invalid_user_id_param

def test_none_idir_user_cannot_search_idir_user(
    test_client_fixture: TestClient,
    test_rsa_key
):
    """
    Test requester is external.
    """

    # override dependency for requester on router.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = \
        mock_get_current_requester_with_none_idir_user

    test_end_point = endPoint_search + f"?user_id={valid_user_id_param}"
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(f"{test_end_point}", headers=jwt_utils.headers(token))

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Action is not allowed for external user." in response.text

def test_search_idir_user_requester_not_found_error_raised(
    test_client_fixture: TestClient,
    test_rsa_key
):
    """
    Test requester does not exist.
    """

    # override dependency for requester not exists.
    app = test_client_fixture.app
    app.dependency_overrides[get_current_requester] = \
        mock_get_current_requester_user_not_exists

    test_end_point = endPoint_search + f"?user_id={valid_user_id_param}"
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(f"{test_end_point}", headers=jwt_utils.headers(token))

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Requester does not exist" in response.text
