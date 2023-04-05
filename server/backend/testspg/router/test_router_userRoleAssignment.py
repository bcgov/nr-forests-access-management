import logging
from http import HTTPStatus

import pytest
import tests.tests.jwt_utils as jwt_utils
from api.app import jwt_validation
from api.app.main import apiPrefix
from fastapi.testclient import TestClient
from sqlmodel import Session
from testspg.constants import (CLIENT_NUMBER_EXISTS_DEACTIVATED,
                               CLIENT_NUMBER_NOT_EXISTS,
                               TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT)

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/user_role_assignment"

FOM_DEV_ADMIN_ROLE = "FOM_DEV_ACCESS_ADMIN"

# TODO: Need to merge and refactor from current postgres tests PR #535


@pytest.fixture(scope="function")
def fom_access_token(test_rsa_key):
    claims = jwt_utils.create_jwt_claims()
    claims[jwt_validation.JWT_GROUPS_KEY] = ["FOM_DEV_ACCESS_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, claims)
    return token


def test_user_role_forest_client_number_not_exist_bad_request(
    test_client_fixture: TestClient,
    fom_access_token,
    dbPgConnection: Session
):
    """
    Test assign user role with none-existing forest client number should be
    rejected.
    """
    client_number_not_exists = CLIENT_NUMBER_NOT_EXISTS
    invalid_request = {
        **TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
        "forest_client_number": client_number_not_exists
    }
    response = test_client_fixture.post(
        f"{endPoint}",
        json=invalid_request,
        headers=jwt_utils.headers(fom_access_token)
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert (f"Forest Client Number {client_number_not_exists} does not exist."
            in response.json()["detail"]
            )


def test_user_role_forest_client_number_inactive_bad_request(
    test_client_fixture: TestClient,
    fom_access_token,
    dbPgConnection: Session
):
    """
    Test assign user role with inactive forest client number should be
    rejected.
    """
    invalid_request = {
        **TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
        "forest_client_number": CLIENT_NUMBER_EXISTS_DEACTIVATED
    }
    response = test_client_fixture.post(
        f"{endPoint}",
        json=invalid_request,
        headers=jwt_utils.headers(fom_access_token)
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert ("Forest Client is not in Active status")
