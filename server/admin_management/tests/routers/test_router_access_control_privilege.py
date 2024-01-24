import logging
from http import HTTPStatus
import starlette.testclient

from api.app.main import apiPrefix
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.routers.router_guards import ERROR_INVALID_ROLE_ID
from tests.constants import (
    TEST_FOREST_CLIENT_NUMBER,
    TEST_FOREST_CLIENT_NUMBER_TWO,
    TEST_FOM_DEV_ADMIN_ROLE,
    TEST_NOT_EXIST_ROLE_ID,
    TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
    TEST_FAM_ADMIN_ROLE,
)
import tests.jwt_utils as jwt_utils


LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/access_control_privileges"


def test_create_access_control_privilege_many(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # test create with invalid role
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FAM_ADMIN_ROLE])
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

    # test create with non exists role id
    token = jwt_utils.create_jwt_token(
        test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE]
    )  # by deafult it will create with FAM admin role
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
            "role_id": TEST_NOT_EXIST_ROLE_ID,
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_INVALID_ROLE_ID) != -1

    # test create access control privilege with abstract role and one forest client number
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert len(data) == 1
    assert data[0].get("status_code") == HTTPStatus.OK

    # test create access control privilege with abstract role and two forest client numbers
    # one just created above, one is new
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
            "forest_client_numbers": [
                TEST_FOREST_CLIENT_NUMBER,
                TEST_FOREST_CLIENT_NUMBER_TWO,
            ],
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert len(data) == 2
    assert data[0].get("status_code") == HTTPStatus.CONFLICT
    assert data[1].get("status_code") == HTTPStatus.OK
