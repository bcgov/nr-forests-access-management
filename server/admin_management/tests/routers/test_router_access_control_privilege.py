import logging
from http import HTTPStatus

import starlette.testclient
import tests.jwt_utils as jwt_utils
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.main import apiPrefix
from api.app.routers.router_guards import (
    ERROR_INVALID_ACCESS_CONTROL_PRIVILEGE_ID, ERROR_INVALID_APPLICATION_ID,
    ERROR_INVALID_ROLE_ID)
from api.app.services.permission_audit_service import PermissionAuditService
from tests.constants import (INVALID_APPLICATION_ID,
                             TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
                             TEST_ACP_CREATE_CONCRETE_BCEID,
                             TEST_APPLICATION_ID_FOM_DEV, TEST_FAM_ADMIN_ROLE,
                             TEST_FOM_DEV_ADMIN_ROLE,
                             TEST_FOREST_CLIENT_NUMBER,
                             TEST_FOREST_CLIENT_NUMBER_TWO,
                             TEST_INACTIVE_FOREST_CLIENT_NUMBER,
                             TEST_NOT_EXIST_APPLICATION_ID,
                             TEST_NOT_EXIST_ROLE_ID,
                             TEST_USER_BUSINESS_GUID_BCEID)

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/access-control-privileges"


def test_create_access_control_privilege_many(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
    mocker
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

    # override router guard dependencies
    override_get_verified_target_user()

    # test create access control privilege with abstract role and one forest client number
    store_delegated_admin_permissions_granted_audit_history_fn_spy = mocker.spy(
        PermissionAuditService, 'store_delegated_admin_permissions_granted_audit_history'
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
        headers=jwt_utils.headers(token),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json().get("assignments_detail")
    assert len(data) == 1
    assert data[0].get("status_code") == HTTPStatus.OK
    assert store_delegated_admin_permissions_granted_audit_history_fn_spy.call_count == 1

    store_delegated_admin_permissions_granted_audit_history_fn_spy.call_count = 0 # reset spy count
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
    data = response.json().get("assignments_detail")
    assert len(data) == 2
    assert data[0].get("status_code") == HTTPStatus.CONFLICT
    assert data[1].get("status_code") == HTTPStatus.OK
    assert store_delegated_admin_permissions_granted_audit_history_fn_spy.call_count == 1

    store_delegated_admin_permissions_granted_audit_history_fn_spy.call_count = 0 # reset spy count
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
    assert store_delegated_admin_permissions_granted_audit_history_fn_spy.call_count == 0


def test_get_access_control_privileges_by_application_id(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
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
    origin_admins_length = len(response.json()["results"])

    # override router guard dependencies
    override_get_verified_target_user()

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
    admins_length = len(response.json()["results"])
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


def test_create_access_control_privilege_bceid_user_update_user_properties(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
    user_service,
):
    # verify user does not exist before creation.
    user = user_service.get_user_by_domain_and_name(
        user_name=TEST_ACP_CREATE_CONCRETE_BCEID["user_name"],
        user_type_code=TEST_ACP_CREATE_CONCRETE_BCEID["user_type_code"],
    )
    assert user is None

    # override router guard dependencies
    mocked_target_bceid_user = {
        **TEST_ACP_CREATE_CONCRETE_BCEID,
        "business_guid": TEST_USER_BUSINESS_GUID_BCEID,
        "first_name": "test",
        "last_name": "bceid",
        "email": "test_bceid@test.com"
    }
    override_get_verified_target_user(mocked_target_bceid_user)

    # create BCeID user/role assignment. Expecting it will save business_guid
    # from mocked_data.business_guid
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.post(
        f"{endPoint}",
        json={**TEST_ACP_CREATE_CONCRETE_BCEID},
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK

    # new user created
    user = user_service.get_user_by_domain_and_name(
        user_name=TEST_ACP_CREATE_CONCRETE_BCEID["user_name"],
        user_type_code=TEST_ACP_CREATE_CONCRETE_BCEID["user_type_code"],
    )
    assert user is not None
    # verify business_guid, first_name, last_name, email are saved to the user.
    assert user.business_guid == TEST_USER_BUSINESS_GUID_BCEID
    assert user.first_name == mocked_target_bceid_user["first_name"]
    assert user.last_name == mocked_target_bceid_user["last_name"]
    assert user.email == mocked_target_bceid_user["email"]


def test_delete_access_control_privilege(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
    mocker
):
    # override router guard dependencies
    override_get_verified_target_user()

    # create an access control privilege with abstract role and one forest client number
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json().get("assignments_detail")[0]["detail"]

    # test delete with invalid role
    store_delegated_admin_permissions_revoked_audit_history_fn_spy = mocker.spy(
        PermissionAuditService, 'store_delegated_admin_permissions_revoked_audit_history'
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.delete(
        f"{endPoint}/{data.get('access_control_privilege_id')}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1
    store_delegated_admin_permissions_revoked_audit_history_fn_spy.call_count == 0

    # test delete access control privilege
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.delete(
        f"{endPoint}/{data.get('access_control_privilege_id')}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    store_delegated_admin_permissions_revoked_audit_history_fn_spy.call_count == 1

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
