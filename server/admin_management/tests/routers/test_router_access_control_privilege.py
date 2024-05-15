import logging
from http import HTTPStatus
import starlette.testclient

from api.app.constants import UserType
from api.app.main import apiPrefix
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.routers.router_guards import (
    ERROR_INVALID_ROLE_ID,
    ERROR_INVALID_APPLICATION_ID,
    ERROR_INVALID_ACCESS_CONTROL_PRIVILEGE_ID,
)
from tests.constants import (
    TEST_FOM_DEV_REVIEWER_ROLE_ID,
    TEST_FOREST_CLIENT_NUMBER,
    TEST_FOREST_CLIENT_NUMBER_TWO,
    TEST_INACTIVE_FOREST_CLIENT_NUMBER,
    TEST_FOM_DEV_ADMIN_ROLE,
    TEST_NOT_EXIST_ROLE_ID,
    TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
    TEST_FAM_ADMIN_ROLE,
    TEST_NOT_EXIST_APPLICATION_ID,
    INVALID_APPLICATION_ID,
    TEST_APPLICATION_ID_FOM_DEV,
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

    # test create access control privilege with invalid forest client numbers
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
            "forest_client_numbers": [
                TEST_FOREST_CLIENT_NUMBER,
                TEST_INACTIVE_FOREST_CLIENT_NUMBER,
            ],
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert str(response.json()["detail"]).find("is not in active status") != -1


def test_get_access_control_privileges_by_application_id(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # test get with invalid role
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{endPoint}?application_id={TEST_APPLICATION_ID_FOM_DEV}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

    # get access control privileges by application id, get original length
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.get(
        f"{endPoint}?application_id={TEST_APPLICATION_ID_FOM_DEV}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    origin_admins_length = len(response.json())
    # create an access control privilege with abstract role and one forest client number
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    # get the application by application id again, verify length adds one
    response = test_client_fixture.get(
        f"{endPoint}?application_id={TEST_APPLICATION_ID_FOM_DEV}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    admins_length = len(response.json())
    assert admins_length == origin_admins_length + 1

    # test get with non exists application id
    response = test_client_fixture.get(
        f"{endPoint}?application_id={TEST_NOT_EXIST_APPLICATION_ID}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_INVALID_APPLICATION_ID) != -1

    # test get with invalid application id
    response = test_client_fixture.get(
        f"{endPoint}?application_id=/{INVALID_APPLICATION_ID}",
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


def test_assign_new_bceid_user_delegated_admin_save_business_guid(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_target_user_bceid_search,
    user_service
):
    ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER = {
        "user_name": "TESTUSER_NOTIN_DB",
        "user_guid": "somerandomguid23AE535428F171BF13",
        "user_type_code": UserType.BCEID,
        "role_id": TEST_FOM_DEV_REVIEWER_ROLE_ID,
    }

    # verify user does not exist before creation.
    user = user_service.get_user_by_domain_and_name(
        user_name=ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER["user_name"],
        user_type_code=ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER["user_type_code"]
    )
    assert user is None

    # override router dependency for "target_user_bceid_search"
    mocked_searched_business_guid = "mockedguid5D4ACA9FA901EE2C91CB3B"
    mocked_data = {
        **ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER,
        "business_guid": mocked_searched_business_guid,
    }

    # override it for test to avoid calling external idim-proxy.
    override_target_user_bceid_search(mocked_data)

    # create BCeID user/role assignment. Expecting it will save business_guid
    # from mocked_data.business_guid
    token = jwt_utils.create_jwt_token(
        test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE]
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK

    # new user created
    user = user_service.get_user_by_domain_and_name(
        user_name=ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER["user_name"],
        user_type_code=ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER["user_type_code"]
    )
    assert user is not None
    # verify business_guid is saved to the user.
    assert user.business_guid == mocked_data["business_guid"]


def test_delete_application_admin(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # create an access control privilege with abstract role and one forest client number
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()[0]["detail"]

    # test delete with invalid role
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.delete(
        f"{endPoint}/{data.get('access_control_privilege_id')}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

    # test delete access control privilege
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.delete(
        f"{endPoint}/{data.get('access_control_privilege_id')}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK

    # test delete non exists access control privilege
    response = test_client_fixture.delete(
        f"{endPoint}/{data.get('access_control_privilege_id')}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert (
        str(response.json()["detail"]).find(ERROR_INVALID_ACCESS_CONTROL_PRIVILEGE_ID)
        != -1
    )
