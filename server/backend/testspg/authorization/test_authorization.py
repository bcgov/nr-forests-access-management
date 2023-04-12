import logging
import starlette.testclient
from api.app.main import apiPrefix
from testspg.jwt_utils import (create_jwt_token,
                               create_jwt_claims,
                               assert_error_response,
                               headers)
from api.app.jwt_validation import (ERROR_GROUPS_REQUIRED,
                                    JWT_GROUPS_KEY)

LOGGER = logging.getLogger(__name__)
fam_applications_endpoint = f"{apiPrefix}/fam_applications"


def test_get_application_missing_groups_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims.pop(JWT_GROUPS_KEY)
    token = create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture_unit.get(f"{fam_applications_endpoint}",
                                            headers=headers(token))

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)


def test_get_application_no_groups_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims[JWT_GROUPS_KEY] = []
    token = create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture_unit.get(f"{fam_applications_endpoint}",
                                            headers=headers(token))

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)
