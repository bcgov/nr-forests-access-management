import logging
from http import HTTPStatus

import starlette.testclient
import tests.jwt_utils as jwt_utils
from api.app.constants import AdminRoleAuthGroup
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.main import apiPrefix
from tests.constants import TEST_APPLICATION_NAME_FAM, TEST_FOM_DEV_ADMIN_ROLE

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/applications"


def test_get_applications(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    # Test no token. Receive 401
    response = test_client_fixture.get(f"{endPoint}")
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    # Test invalid role. (Only FAM admin role is allowed) Receive 403
    token = jwt_utils.create_jwt_token(test_rsa_key, [TEST_FOM_DEV_ADMIN_ROLE])
    response = test_client_fixture.get(
        f"{endPoint}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    assert str(response.json()["detail"]).find(ERROR_PERMISSION_REQUIRED) != -1

    # Test valid role (FAM_ADMIN) can get applications
    token = jwt_utils.create_jwt_token(test_rsa_key, [AdminRoleAuthGroup.FAM_ADMIN])
    response = test_client_fixture.get(
        f"{endPoint}",
        headers=jwt_utils.headers(token)
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) != 0
    # - Verify following keys are in return.
    assert 'application_name' in data[0].keys()
    assert 'application_description' in data[0].keys()
    assert 'app_environment' in data[0].keys()
    assert 'application_id' in data[0].keys()
    # - Verify list contains application "FAM"
    assert any(TEST_APPLICATION_NAME_FAM in x.values() for x in data)
