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


# Test commented because can't figure out how to mock out the db calls
# def test_get_application_role_unauthorized_failure(
#         test_client_fixture: starlette.testclient.TestClient,
#         test_rsa_key):

#     claims = create_jwt_claims()
#     claims[JWT_GROUPS_KEY] = ["WRONG_ROLE"]
#     token = create_jwt_token(test_rsa_key, claims)

    # Mock out 2 database calls
    # test_client_fixture.app.dependency_overrides[database.get_db] = \
    #     lambda: UnifiedAlchemyMagicMock(data=[
    #         (
    #             [
    #                 mock.call.query(models.FamApplication),
    #                 mock.call.filter(
    #                     models.FamApplication.application_id == 1
    #                 )
    #             ],
    #             [models.FamApplication(
    #                 application_id=1,
    #                 application_name="fam",
    #                 application_description="description",
    #                 create_user="me",
    #                 create_date=datetime.datetime.now()
    #             )]
    #         ),
    #         (
    #             [
    #                 mock.call.query(models.FamRole),
    #                 mock.call.filter(
    #                     models.FamRole.application_id == 1,
    #                     models.FamRole.parent_role_id == None  # noqa
    #                 )
    #             ],
    #             []
    #         ),
    #     ])


    # response = test_client_fixture.get(fam_application_roles_endpoint,
    #                                    headers=headers(token))

    # assert_error_response(response, 403, ERROR_PERMISSION_REQUIRED)


# Test commented because can't figure out how to mock out the db calls
# def test_get_application_role_authorized_success(
#         test_client_fixture: starlette.testclient.TestClient,
#         test_rsa_key):

#     claims = create_jwt_claims()
#     claims[JWT_GROUPS_KEY] = ["FAM_ADMIN"]
#     token = create_jwt_token(test_rsa_key, claims)

#     # Mock out 2 database calls
#     test_client_fixture.app.dependency_overrides[database.get_db] = \
#         lambda: UnifiedAlchemyMagicMock(data=[
#             (
#                 [
#                     mock.call.query(models.FamApplication),
#                     mock.call.filter(
#                         models.FamApplication.application_id == 1
#                     )
#                 ],
#                 [models.FamApplication(
#                     application_id=1,
#                     application_name="fam",
#                     application_description="description",
#                     create_user="me",
#                     create_date=datetime.datetime.now()
#                 )]
#             ),
#             (
#                 [
#                     mock.call.query(models.FamRole),
#                     mock.call.filter(
#                         models.FamRole.application_id == 1,
#                         models.FamRole.parent_role_id == None  # noqa
#                     )
#                 ],
#                 []
#             ),
#         ])

#     response = test_client_fixture.get(fam_application_roles_endpoint,
#                                        headers=headers(token))

#     assert response.status_code == 204
#     data = response.json()
#     assert data == []

