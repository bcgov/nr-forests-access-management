import logging
import starlette.testclient
from api.app.main import apiPrefix
from tests.jwt_utils import (
    create_jwt_token,
    create_jwt_claims,
    assert_error_response,
    headers,
)
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED, JWT_GROUPS_KEY

LOGGER = logging.getLogger(__name__)
smoke_test_endpoint = (
    f"{apiPrefix}/smoke_test"  # todo: update this to a real endpoint later
)


def test_smoke_test_not_fam_admin_failure(
    test_client_fixture_unit: starlette.testclient.TestClient, test_rsa_key
):

    claims = create_jwt_claims()
    claims[JWT_GROUPS_KEY] = []
    token = create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture_unit.get(
        f"{smoke_test_endpoint}", headers=headers(token)
    )

    assert_error_response(response, 403, ERROR_PERMISSION_REQUIRED)
