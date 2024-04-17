import copy
import logging
from http import HTTPStatus

import pytest
import starlette.testclient
import testspg.db_test_utils as db_test_utils
import testspg.jwt_utils as jwt_utils
from api.app.constants import UserType
from api.app.crud import crud_application, crud_role, crud_user, crud_user_role
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.main import apiPrefix
from api.app.routers.router_guards import (
    ERROR_SELF_GRANT_PROHIBITED,
    ERROR_DIFFERENT_ORG_GRANT_PROHIBITED,
)
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from testspg.constants import (
    CLIENT_NUMBER_EXISTS_ACTIVE_00001011,
    CLIENT_NUMBER_EXISTS_ACTIVE,
    CLIENT_NUMBER_EXISTS_DEACTIVATED,
    CLIENT_NUMBER_NOT_EXISTS,
    TEST_FOM_DEV_APPLICATION_ID,
    TEST_FOM_DEV_REVIEWER_ROLE_ID,
    TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    TEST_FOM_TEST_APPLICATION_ID,
    TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
    TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
    TEST_USER_ROLE_ASSIGNMENT_FOM_TEST_CONCRETE,
    TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE_BCEID,
    TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT_BCEID,
)

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/user_role_assignment"

FOM_DEV_ADMIN_ROLE = "FOM_DEV_ADMIN"
FOM_TEST_ADMIN_ROLE = "FOM_TEST_ADMIN"
ERROR_DUPLICATE_USER_ROLE = "Role already assigned to user."


@pytest.fixture(scope="function")
def fom_dev_access_admin_token(test_rsa_key):
    access_roles = [FOM_DEV_ADMIN_ROLE]
    return jwt_utils.create_jwt_token(test_rsa_key, access_roles)


@pytest.fixture(scope="function")
def fom_test_access_admin_token(test_rsa_key):
    access_roles = [FOM_TEST_ADMIN_ROLE]
    return jwt_utils.create_jwt_token(test_rsa_key, access_roles)


# helper method
def create_test_user_role_assignment(
    test_client_fixture: starlette.testclient.TestClient, token, requestBody
):
    # create a user role assignment used for testing
    response = test_client_fixture.post(
        f"{endPoint}",
        json=requestBody,
        headers=jwt_utils.headers(token),
    )
    data = response.json()
    return data["user_role_xref_id"]


# note: this might need to be a real idir username
# and a real forest client id
# once we enable the verifiy idir feature
# and the verify of forest client id feature
TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_DIFF_ROLE = {
    "user_name": "fom_user_test",
    "user_type_code": "I",
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": CLIENT_NUMBER_EXISTS_ACTIVE,
}
TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_DIFF_FCN = {
    "user_name": "fom_user_test",
    "user_type_code": "I",
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": CLIENT_NUMBER_EXISTS_ACTIVE_00001011,
}


# ------------------ test create user role assignment ----------------------- #
def test_create_user_role_assignment_not_authorized(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    """
    test user has no authentication to the app
    user without FOM_DEV_ADMIN role and not delegated admin of FOM DEV cannot grant FOM_DEV roles
    """
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert data["detail"]["description"] == "Requester has no admin or delegated admin access to the application."


def test_create_user_role_assignment_with_concrete_role_authorize_by_delegated_admin(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
):
    """
    test if user is not app admin, but is delegated admin with the correct privilege, will be able to grant access

    this test case uses business bceid user with FOM DEV FOM_REVIEWER privilege as example
    test if business bceid user is delegated admin of FOM DEV for FOM_REVIEWER role,
    able to grant FOM_REVIEWER access to a business bceid user from same org
    """
    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, [], jwt_utils.COGNITO_USERNAME_BCEID
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE_BCEID,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert "user_role_xref_id" in data
    assert "user_id" in data
    assert "role_id" in data
    assert "application_id" in data


def test_create_user_role_assignment_with_abstract_role_authorize_by_delegated_admin(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
):
    """
    test if user is not app admin, but is delegated admin with the correct privilege, will be able to grant access

    this test case uses business bceid user with FOM DEV FOM_SUBMITTER_00001018 privilege as example
    test if business bceid user is delegated admin of FOM DEV for FOM_SUBMITTER role with forest client number 00001018,
    able to grant FOM_SUBMITTER_00001018 access for business bceid user from same org,
    will not be able to grant access with other forest client numbers like FOM_SUBMITTER_00001011
    """
    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, [], jwt_utils.COGNITO_USERNAME_BCEID
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT_BCEID,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert "user_role_xref_id" in data
    assert "user_id" in data
    assert "role_id" in data
    assert "application_id" in data

    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT_BCEID,
            "forest_client_number": CLIENT_NUMBER_EXISTS_ACTIVE_00001011,
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user has no privilege to grant FOM_SUBMITTER access with forest client number 00001011
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert data["detail"]["description"] == "Requester has no privilege to grant this access."


def test_create_user_role_assignment_bceid_cannot_grant_idir_access(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
):
    """
    test business bceid user cannnot grant idir user access
    """
    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, roles=[], username=jwt_utils.COGNITO_USERNAME_BCEID
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user cannot grant idir user access
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert data["detail"]["description"] == "Business BCEID requester has no privilege to grant this access to IDIR user."


def test_create_user_role_assignment_bceid_cannot_grant_access_from_diff_org(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
):
    """
    test business bceid user cannnot grant business bceid user access from different organization
    """
    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, roles=[], username=jwt_utils.COGNITO_USERNAME_BCEID
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE_BCEID,
            "user_name": "LOAD-4-TEST",  # Business bceid user LOAD-4-TEST is already created in local_sql with business_guid
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user cannot grant business bceid user access from different organization
    assert data["detail"]["code"] == ERROR_DIFFERENT_ORG_GRANT_PROHIBITED
    assert data["detail"]["description"] == "Managing for different organization is not allowed."


def test_create_user_role_assignment_with_concrete_role(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    db_pg_session: Session,
):
    """
    test assign a concrete role to a user
    """
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert "user_role_xref_id" in data
    assert "user_id" in data
    assert "role_id" in data
    assert "application_id" in data

    # verify assignment did get created
    assignment_user_role_concrete = crud_application.get_application_role_assignments(
        db_pg_session, data["application_id"]
    )
    assert len(assignment_user_role_concrete) == 1
    assert (
        assignment_user_role_concrete[0].user_role_xref_id == data["user_role_xref_id"]
    )

    # verify assignment linking to correct user
    assignment_user = crud_user.get_user(
        db_pg_session, assignment_user_role_concrete[0].user_id
    )
    assert assignment_user is not None

    # verify assignment linking to correct role and parent role
    assignment_role = crud_role.get_role(
        db_pg_session, assignment_user_role_concrete[0].role_id
    )
    assert assignment_role is not None
    assert assignment_role.parent_role_id is None

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{data['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_create_user_role_assignment_with_concrete_role_duplicate(
    test_client_fixture: starlette.testclient.TestClient, fom_dev_access_admin_token
):
    """
    test assign same role for the same user
    """
    # create user role assignment the first time
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # create user role assignment the second time
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == 409
    assert response.json()["detail"] == ERROR_DUPLICATE_USER_ROLE

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{data['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_create_user_role_assignment_with_abstract_role_without_forestclient(
    test_client_fixture: starlette.testclient.TestClient, fom_dev_access_admin_token
):
    """
    test assign an abscrate role to a user without forest client number
    """
    COPY_TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT = copy.deepcopy(
        TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT
    )
    COPY_TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT.pop("forest_client_number")
    response = test_client_fixture.post(
        f"{endPoint}",
        json=COPY_TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Invalid role assignment request. "
        + "Cannot assign user "
        + TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT["user_name"]
        + " to abstract role FOM_SUBMITTER"
    )


def test_create_user_role_assignment_with_abstract_role(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    db_pg_session: Session,
):
    """
    test assign an abscrate role to a user
    """
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json()
    assert "user_role_xref_id" in data
    assert "user_id" in data
    assert "role_id" in data
    assert "application_id" in data

    # verify assignment did get created
    assignment_user_role_abstract = crud_application.get_application_role_assignments(
        db_pg_session, data["application_id"]
    )
    assert len(assignment_user_role_abstract) == 1
    assert (
        assignment_user_role_abstract[0].user_role_xref_id == data["user_role_xref_id"]
    )

    # verify assignment linking to correct user
    assignment_user = crud_user.get_user(
        db_pg_session, assignment_user_role_abstract[0].user_id
    )
    assert assignment_user is not None

    # verify assignment linking to correct role and parent role
    assignment_role = crud_role.get_role(
        db_pg_session, assignment_user_role_abstract[0].role_id
    )
    assert assignment_role is not None
    assert assignment_role.parent_role_id == TEST_FOM_DEV_SUBMITTER_ROLE_ID

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{data['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_create_user_role_assignment_with_same_username(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    db_pg_session: Session,
):
    # create a user role assignment
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    assignment_one = response.json()

    # allow create a user role assignment with the same username, different role
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_DIFF_ROLE,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    assignment_two = response.json()

    # allow create a user role assignment with the same username, different role
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_DIFF_FCN,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    assignment_three = response.json()

    assignment_user_role_items = crud_application.get_application_role_assignments(
        db_pg_session, assignment_one["application_id"]
    )
    assert len(assignment_user_role_items) == 3

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{assignment_one['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = test_client_fixture.delete(
        f"{endPoint}/{assignment_two['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = test_client_fixture.delete(
        f"{endPoint}/{assignment_three['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_assign_same_application_roles_for_different_environments(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    fom_test_access_admin_token,
    db_pg_session: Session,
):
    # create a user role assignment
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    fom_dev_user_role_assignment = response.json()
    assert "user_role_xref_id" in fom_dev_user_role_assignment

    # create a user role assignment with same username and type, but for FOM_TEST role
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_TEST_CONCRETE,
        headers=jwt_utils.headers(fom_test_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    fom_test_user_role_assignment = response.json()
    assert "user_role_xref_id" in fom_test_user_role_assignment

    # verify assignment id not the same
    assignment_user_role_id_dev = fom_dev_user_role_assignment["user_role_xref_id"]
    assignment_user_role_id_test = fom_test_user_role_assignment["user_role_xref_id"]
    assert assignment_user_role_id_dev != assignment_user_role_id_test

    # verify role id not the same
    assignment_role_id_dev = fom_dev_user_role_assignment["role_id"]
    assignment_role_id_test = fom_test_user_role_assignment["role_id"]
    assert assignment_role_id_dev != assignment_role_id_test

    # verify application id
    assert fom_dev_user_role_assignment["application_id"] == TEST_FOM_DEV_APPLICATION_ID
    assert (
        fom_test_user_role_assignment["application_id"] == TEST_FOM_TEST_APPLICATION_ID
    )

    # verify assignment did get created for fom_dev
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db_pg_session, TEST_FOM_DEV_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 1
    assert (
        assignment_user_role_items[0].user_role_xref_id
        == fom_dev_user_role_assignment["user_role_xref_id"]
    )

    # verify assignment did get created for fom_test
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db_pg_session, TEST_FOM_TEST_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 1
    assert (
        assignment_user_role_items[0].user_role_xref_id
        == fom_test_user_role_assignment["user_role_xref_id"]
    )

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{fom_dev_user_role_assignment['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    # verify no user role assignment for fom_dev, but still have one for fom_test
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db_pg_session, TEST_FOM_DEV_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 0
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db_pg_session, TEST_FOM_TEST_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 1

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{fom_test_user_role_assignment['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_test_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    # verify no user role assignment for fom_test
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db_pg_session, TEST_FOM_TEST_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 0


def test_user_role_forest_client_number_not_exist_bad_request(
    test_client_fixture: TestClient, fom_dev_access_admin_token
):
    """
    Test assign user role with none-existing forest client number should be
    rejected.
    """
    client_number_not_exists = CLIENT_NUMBER_NOT_EXISTS
    invalid_request = {
        **TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
        "forest_client_number": client_number_not_exists,
    }
    response = test_client_fixture.post(
        f"{endPoint}",
        json=invalid_request,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert (
        f"Forest Client Number {client_number_not_exists} does not exist."
        in response.json()["detail"]
    )


def test_user_role_forest_client_number_inactive_bad_request(
    test_client_fixture: TestClient, fom_dev_access_admin_token
):
    """
    Test assign user role with inactive forest client number should be
    rejected.
    """
    invalid_request = {
        **TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
        "forest_client_number": CLIENT_NUMBER_EXISTS_DEACTIVATED,
    }
    response = test_client_fixture.post(
        f"{endPoint}",
        json=invalid_request,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert "Forest Client is not in Active status"


def test_self_grant_fail(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    db_pg_session: Session,
):
    # Setup challenge: The user in the json sent to the service must match the user
    # in the JWT security token.
    user_role_assignment_request_data = {
        "user_name": jwt_utils.IDIR_USERNAME,
        "user_type_code": UserType.IDIR,
        "role_id": TEST_FOM_DEV_REVIEWER_ROLE_ID,
    }

    response = test_client_fixture.post(
        f"{endPoint}",
        json=user_role_assignment_request_data,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )

    row = db_test_utils.get_user_role_by_cognito_user_id_and_role_id(
        db_pg_session, jwt_utils.COGNITO_USERNAME, TEST_FOM_DEV_REVIEWER_ROLE_ID
    )
    assert row is None, "Expected user role assignment not to be created"

    jwt_utils.assert_error_response(response, 403, ERROR_SELF_GRANT_PROHIBITED)


# ---------------- Test delete user role assignment ------------ #


def test_delete_user_role_assignment_not_authorized(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
):
    """
    test if user is not app admin, and not app delegated admin, can not remove user role assginments of the application

    this test case uses FOM DEV as example
    test if user is not app admin and not delegated admin of FOM DEV, cannot remove FOM DEV user role assginments
    """
    # create a user role assignment
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
    )

    # create a token for idir user without any app admin roles and no delegated admin privilege
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[])
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert data["detail"]["description"] == "Requester has no admin or delegated admin access to the application."


def test_deleter_user_role_assignment_authorize_by_delegated_admin(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
):
    """
    test if user is not app admin, but is delegated admin with the correct privilege, will be able to remove access

    this test case uses business bceid user with FOM DEV FOM_REVIEWER privilege as example
    test if business bceid user is delegated admin of FOM DEV for FOM_REVIEWER role,
    able to remove FOM_REVIEWER access for business bceid user from same org
    """
    # create a user role assignment for a business bceid user within the same organization as the user COGNITO_USERNAME_BCEID
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE_BCEID,
    )

    # create a token for business bceid user COGNITO_USERNAME_BCEID without any app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, roles=[], username=jwt_utils.COGNITO_USERNAME_BCEID
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    # delete is successful
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_role_assignment_with_forest_client_number(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
):
    """
    test if user is not app admin, but is delegated admin with the correct privilege, will be able to remove access

    this test case uses business bceid user with FOM DEV FOM_SUBMITTER_00001018 privilege as example
    test if business bceid user is delegated admin of FOM DEV for FOM_SUBMITTER role with forest client number 00001018,
    able to remove FOM_SUBMITTER_00001018 access for business bceid user from same org,
    will not be able to remove access with other forest client numbers like FOM_SUBMITTER_00001011
    """
    # create a user role assignment for a business bceid user within the same organization as the user COGNITO_USERNAME_BCEID
    # with abstract role FOM_SUBMITTER and forest client number 00001018
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT_BCEID,
    )

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, [], jwt_utils.COGNITO_USERNAME_BCEID
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    # delete is successful
    assert response.status_code == HTTPStatus.NO_CONTENT

    # create a user role assignment for a business bceid user within the same organization as the user COGNITO_USERNAME_BCEID
    # with abstract role FOM_SUBMITTER and forest client number 00001011
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        {
            **TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT_BCEID,
            "forest_client_number": "00001011",
        },
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user has no privilege to delete role with forest client number 00001011
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert data["detail"]["description"] == "Requester has no privilege to grant this access."


def test_deleter_user_role_assignment_bceid_cannot_delete_idir_access(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
):
    """
    test business bceid user cannnot delete idir user access
    """
    # create a user role assignment for IDIR user
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
    )

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, roles=[], username=jwt_utils.COGNITO_USERNAME_BCEID
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user cannot delete idir user access
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert data["detail"]["description"] == "Business BCEID requester has no privilege to grant this access to IDIR user."


def test_deleter_user_role_assignment_bceid_cannot_delete_access_from_diff_org(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
):
    """
    test business bceid user cannnot delete business bceid user access from different organization
    """
    # create a user role assignment for a business bceid user from diff organization as the user COGNITO_USERNAME_BCEID
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        {
            **TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE_BCEID,
            "user_name": "LOAD-4-TEST",  # we created this user with business_guid in local_sql
        },
    )

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, roles=[], username=jwt_utils.COGNITO_USERNAME_BCEID
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user cannot delete business bceid user access from different organization
    assert data["detail"]["code"] == ERROR_DIFFERENT_ORG_GRANT_PROHIBITED
    assert data["detail"]["description"] == "Managing for different organization is not allowed."


def test_delete_user_role_assignment(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    db_pg_session: Session,
):
    # create a user role assignment
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "user_role_xref_id" in data

    # verify assignment did get created
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db_pg_session, data["application_id"]
    )
    assert len(assignment_user_role_items) == 1
    assert assignment_user_role_items[0].user_role_xref_id == data["user_role_xref_id"]

    # execute Delete
    response = test_client_fixture.delete(
        f"{endPoint}/{data['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    # verify user/role assignment has been deleted
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db_pg_session, data["application_id"]
    )
    assert len(assignment_user_role_items) == 0


def test_self_remove_grant_fail(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    db_pg_session: Session,
):

    # Setup: the user_role_assignment record already exists
    # It should NOT get deleted
    user = crud_user.get_user_by_cognito_user_id(
        db=db_pg_session, cognito_user_id=jwt_utils.COGNITO_USERNAME
    )
    user_role = crud_user_role.create(
        db=db_pg_session,
        user_id=user.user_id,
        role_id=TEST_FOM_DEV_REVIEWER_ROLE_ID,
        requester=jwt_utils.COGNITO_USERNAME,
    )

    response = test_client_fixture.delete(
        f"{endPoint}/{user_role.user_role_xref_id}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )

    row = db_test_utils.get_user_role_by_cognito_user_id_and_role_id(
        db_pg_session, jwt_utils.COGNITO_USERNAME, TEST_FOM_DEV_REVIEWER_ROLE_ID
    )
    assert row is not None, "Expected user role assignment not to be deleted"

    jwt_utils.assert_error_response(response, 403, ERROR_SELF_GRANT_PROHIBITED)
