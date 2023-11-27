import logging
import pytest
from pydantic import ValidationError
from http import HTTPStatus
import starlette.testclient

from api.app import schemas
from api.app.main import apiPrefix

from tests.constants import (
    TEST_NEW_APPLICATION_ADMIN,
    TEST_NOT_INVALID_USER_TYPE,
    TEST_NOT_INVALID_USER_TYPE,
    TEST_NEW_APPLICATION_ADMIN,
    TEST_NOT_EXIST_APPLICATION_ID
)
import tests.jwt_utils as jwt_utils


LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/application_admin"


def test_create_application_admin(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # test create application admin
    token = jwt_utils.create_jwt_token(
        test_rsa_key
    )  # by deafult it will create with FAM admin role
    response = test_client_fixture.post(
        f"{endPoint}", json=TEST_NEW_APPLICATION_ADMIN, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert data.get("application_id") == TEST_NEW_APPLICATION_ADMIN.get(
        "application_id"
    )

    # test create duplicate application admin
    token = jwt_utils.create_jwt_token(
        test_rsa_key
    )  # by deafult it will create with FAM admin role
    response = test_client_fixture.post(
        f"{endPoint}", json=TEST_NEW_APPLICATION_ADMIN, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() is not None
    assert str(response.json()["detail"]).find("User is admin already") != -1

    # test create with invalid user type
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            "user_type_code": TEST_NOT_INVALID_USER_TYPE,
            "user_name": TEST_NEW_APPLICATION_ADMIN.get("user_name"),
            "application_id": TEST_NEW_APPLICATION_ADMIN.get("application_id"),
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() is not None
    assert str(response.json()["detail"]).find("Input should be 'I' or 'B'") != -1

    # test create with invalid application id
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            "user_type_code": TEST_NEW_APPLICATION_ADMIN.get("user_type_code"),
            "user_name": TEST_NEW_APPLICATION_ADMIN.get("user_name"),
            "application_id": TEST_NOT_EXIST_APPLICATION_ID,
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert str(response.json()["detail"]).find("invalid_application_id") != -1
