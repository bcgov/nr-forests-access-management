import logging
import starlette.testclient
import mock
import datetime
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from api.app.main import apiPrefix
from api.app import database
from api.app.models import model as models
from tests.jwt_utils import (create_jwt_access_token,
                             create_jwt_access_claims,
                             assert_error_response,
                             headers)

from api.app.jwt_validation import (ERROR_GROUPS_REQUIRED,
                                    ERROR_PERMISSION_REQUIRED,
                                    JWT_GROUPS_KEY)

LOGGER = logging.getLogger(__name__)
fam_applications_endpoint = f"{apiPrefix}/fam_applications"


def test_get_application_missing_groups_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key,
        test_id_token):

    claims = create_jwt_access_claims()
    claims.pop(JWT_GROUPS_KEY)
    access_token = create_jwt_access_token(test_rsa_key, claims)

    response = test_client_fixture_unit.get(f"{fam_applications_endpoint}",
                                            headers=headers(test_id_token, access_token))

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)


def test_get_application_no_groups_failure(
        test_client_fixture_unit: starlette.testclient.TestClient,
        test_rsa_key,
        test_id_token):

    claims = create_jwt_access_claims()
    claims[JWT_GROUPS_KEY] = []
    access_token = create_jwt_access_token(test_rsa_key, claims)

    response = test_client_fixture_unit.get(f"{fam_applications_endpoint}",
                                            headers=headers(test_id_token, access_token))

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)
