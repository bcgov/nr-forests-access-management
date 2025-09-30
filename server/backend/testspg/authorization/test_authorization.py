import logging

import starlette.testclient
from api.app.jwt_validation import (ERROR_GROUPS_REQUIRED,
                                    ERROR_PERMISSION_REQUIRED, JWT_GROUPS_KEY)
from api.app.main import internal_api_prefix
from testspg.constants import (FC_NUMBER_EXISTS_ACTIVE_00000001,
                               FOM_DEV_APPLICATION_ID)
from testspg.jwt_utils import (assert_error_response, create_jwt_claims,
                               create_jwt_token, headers)

LOGGER = logging.getLogger(__name__)

# we don't have any delegated admin in the clean db, this test mainly focus on the token
# the GET user role assignment endpoint requires requester to be the app admin or delegated admin of FOM DEV
get_user_role_assignment_endpoint = (
    f"{internal_api_prefix}/fam-applications/{FOM_DEV_APPLICATION_ID}/user-role-assignment"
)
# the search forest client number endpoint requires requester be the app admin or delegated admin of at least one app
search_forest_client_endpoint = (
    f"{internal_api_prefix}/forest-clients/search?client_number={FC_NUMBER_EXISTS_ACTIVE_00000001}"
)


def test_get_user_role_assignment_miss_access_to_app_failure(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):

    claims = create_jwt_claims()
    claims.pop(JWT_GROUPS_KEY)
    token = create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
        f"{get_user_role_assignment_endpoint}", headers=headers(token)
    )

    assert_error_response(response, 403, ERROR_PERMISSION_REQUIRED)


def test_get_user_role_assignment_no_access_to_app_failure(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):

    claims = create_jwt_claims()
    claims[JWT_GROUPS_KEY] = []
    token = create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
        f"{get_user_role_assignment_endpoint}", headers=headers(token)
    )

    assert_error_response(response, 403, ERROR_PERMISSION_REQUIRED)


def test_search_forest_client_miss_access_failure(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):

    claims = create_jwt_claims()
    claims.pop(JWT_GROUPS_KEY)
    token = create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
        f"{search_forest_client_endpoint}", headers=headers(token)
    )

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)


def test_get_user_role_assignment_no_access_failure(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):

    claims = create_jwt_claims()
    claims[JWT_GROUPS_KEY] = []
    token = create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
        f"{search_forest_client_endpoint}", headers=headers(token)
    )

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)
