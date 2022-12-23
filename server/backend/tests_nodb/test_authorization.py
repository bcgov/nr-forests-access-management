import logging
import starlette.testclient
import mock
import datetime
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from api.app.main import apiPrefix
from api.app import database
from api.app.models import model as models
from .jwt_utils import (create_jwt_token,
                        create_jwt_claims,
                        assert_error_response,
                        headers)

from api.app.jwt_validation import (ERROR_GROUPS_REQUIRED,
                                    ERROR_PERMISSION_REQUIRED,
                                    JWT_GROUPS_KEY)

LOGGER = logging.getLogger(__name__)
fam_applications_endpoint = f"{apiPrefix}/fam_applications/authorize"

test_role_id = 1
fam_application_roles_endpoint = f"{apiPrefix}/fam_applications/{test_role_id}/fam_roles/authorize"


def test_get_application_missing_groups_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims.pop(JWT_GROUPS_KEY)
    token = create_jwt_token(test_rsa_key, claims)

    response = test_client_fixture.get(f"{fam_applications_endpoint}",
                                       headers=headers(token))

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)


def test_get_application_no_groups_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims[JWT_GROUPS_KEY] = []
    token = create_jwt_token(test_rsa_key, claims)

    response = test_client_fixture.get(f"{fam_applications_endpoint}",
                                       headers=headers(token))

    assert_error_response(response, 403, ERROR_GROUPS_REQUIRED)


def test_get_application_role_unauthorized_failure(
        test_client_fixture: starlette.testclient.TestClient,
        test_rsa_key):

    claims = create_jwt_claims()
    claims[JWT_GROUPS_KEY] = ["WRONG_ROLE"]
    token = create_jwt_token(test_rsa_key, claims)

    response = test_client_fixture.get(fam_application_roles_endpoint,
                                       headers=headers(token))

    assert_error_response(response, 403, ERROR_PERMISSION_REQUIRED)




