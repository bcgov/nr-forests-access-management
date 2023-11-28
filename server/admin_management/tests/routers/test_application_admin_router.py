import logging
from http import HTTPStatus
import starlette.testclient

from api.app.main import apiPrefix
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.routers.router_guards import (
    ERROR_INVALID_APPLICATION_ID,
    ERROR_INVALID_APPLICATION_ADMIN_ID,
)

from tests.constants import (
    TEST_NEW_APPLICATION_ADMIN,
    TEST_NOT_INVALID_USER_TYPE,
    TEST_NOT_INVALID_USER_TYPE,
    TEST_NEW_APPLICATION_ADMIN,
    TEST_NOT_EXIST_APPLICATION_ID,
    TEST_APPLICATION_ID_FAM,
    TEST_FOM_DEV_ADMIN_ROLE,
    INVALID_APPLICATION_ID,
)
import tests.jwt_utils as jwt_utils


LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/application_admin"


def test_create_application_admin(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # test create with invalid role
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.post(
        f"{endPoint}", json=TEST_NEW_APPLICATION_ADMIN, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

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

    # test create with non exists application id
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
    assert str(response.json()["detail"]).find(ERROR_INVALID_APPLICATION_ID) != -1


def test_delete_application_admin(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # create an application admin first
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.post(
        f"{endPoint}", json=TEST_NEW_APPLICATION_ADMIN, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert data.get("application_id") == TEST_NEW_APPLICATION_ADMIN.get(
        "application_id"
    )

    # test delete with invalid role
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.delete(
        f"{endPoint}/{data['application_admin_id']}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

    # test delete application admin
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.delete(
        f"{endPoint}/{data['application_admin_id']}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK

    # test delete non exists application admin
    response = test_client_fixture.delete(
        f"{endPoint}/{data['application_admin_id']}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_INVALID_APPLICATION_ADMIN_ID) != -1


def test_get_application_admin_by_application_id(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # test get with invalid role
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.get(
        f"{endPoint}/{TEST_APPLICATION_ID_FAM}/admins", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

    # get application admin by application id, get original length
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{endPoint}/{TEST_APPLICATION_ID_FAM}/admins",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    origin_admins_length = len(response.json())
    # create an application admin
    response = test_client_fixture.post(
        f"{endPoint}", json=TEST_NEW_APPLICATION_ADMIN, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert data.get("application_id") == TEST_NEW_APPLICATION_ADMIN.get(
        "application_id"
    )
    # get the application by application id again, verify length adds one
    response = test_client_fixture.get(
        f"{endPoint}/{TEST_APPLICATION_ID_FAM}/admins",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    admins_length = len(response.json())
    assert admins_length == origin_admins_length + 1

    # test get with non exists application id
    response = test_client_fixture.get(
        f"{endPoint}/{TEST_NOT_EXIST_APPLICATION_ID}/admins",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    assert len(response.json()) == 0

    # test get with invalid application id
    response = test_client_fixture.get(
        f"{endPoint}/{INVALID_APPLICATION_ID}/admins",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() is not None
    assert (
        str(response.json()["detail"]).find(
            "Input should be a valid integer, unable to parse string as an integer"
        )
        != -1
    )
