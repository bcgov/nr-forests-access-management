import logging
import copy
import starlette.testclient
from sqlalchemy.orm import Session
from api.app.main import apiPrefix
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.crud import crud_application
from api.app.crud import crud_user
from api.app.crud import crud_role
import testspg.jwt_utils as jwt_utils
from testspg.constants import TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE, \
    TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT, \
    TEST_USER_ROLE_ASSIGNMENT_FOM_TEST_CONCRETE, \
    TEST_FOM_DEV_SUBMITTER_ROLE_ID, \
    TEST_FOM_DEV_APPLICATION_ID, \
    TEST_FOM_TEST_APPLICATION_ID, \
    TEST_NOT_EXIST_USER_TYPE

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/user_role_assignment"

FOM_DEV_ADMIN_ROLE = "FOM_DEV_ACCESS_ADMIN"
FOM_TEST_ADMIN_ROLE = "FOM_TEST_ACCESS_ADMIN"
ERROR_DUPLICATE_USER_ROLE = "Role already assigned to user."


TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_DIFF_ROLE = {
    # todo: this might need to be a real idir username
    # once we enable the verifiy idir feature
    "user_name": "fom_user_test",
    "user_type_code": "I",
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": "00000002"
}
TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_DIFF_FCN = {
    # todo: this might need to be a real idir username
    # once we enable the verifiy idir feature
    "user_name": "fom_user_test",
    "user_type_code": "I",
    "role_id": TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    "forest_client_number": "00000003"
}


def test_create_user_role_assignment_not_authorized(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    """
    test user has no authentication to the app
    user without FOM_DEV_ACCESS_ADMIN role cannot grant FOM_DEV roles
    """
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 403
    assert response.json() is not None
    data = response.json()
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED


def test_create_user_role_assignment_with_concrete_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    dbPgSession: Session
):
    """
    test assign a concrete role to a user
    """
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    assert response.json() is not None
    data = response.json()
    assert "user_role_xref_id" in data
    assert "user_id" in data
    assert "role_id" in data
    assert "application_id" in data

    # verify assignment did get created
    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, data["application_id"]
    )
    assert len(assignment_user_role_items) == 1
    assert assignment_user_role_items[0].user_role_xref_id == data["user_role_xref_id"]

    # verify assignment linking to correct user
    assignment_user = crud_user.get_user(
        dbPgSession, assignment_user_role_items[0].user_id
    )
    assert assignment_user is not None

    # verify assignment linking to correct role and parent role
    assignment_role = crud_role.get_role(
        dbPgSession, assignment_user_role_items[0].role_id
    )
    assert assignment_role is not None
    assert assignment_role.parent_role_id is None

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{data['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204


def test_create_user_role_assignment_with_concrete_role_duplicate(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    """
    test assign same role for the same user
    """
    # create user role assignment the first time
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    data = response.json()

    # create user role assignment the second time
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 409
    assert response.json()["detail"] == ERROR_DUPLICATE_USER_ROLE

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{data['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204


def test_create_user_role_assignment_with_abstract_role_without_forestclient(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
):
    """
    test assign an abscrate role to a user without forest client number
    """
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    COPY_TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT = \
        copy.deepcopy(TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT)
    COPY_TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT.pop("forest_client_number")
    response = test_client_fixture.post(
        f"{endPoint}",
        json=COPY_TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid role assignment request. " + \
        "Cannot assign user " + \
        TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT["user_name"] + \
        " to abstract role FOM_SUBMITTER"


def test_create_user_role_assignment_with_abstract_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    dbPgSession: Session
):
    """
    test assign an abscrate role to a user
    """
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    assert response.json() is not None
    data = response.json()
    assert "user_role_xref_id" in data
    assert "user_id" in data
    assert "role_id" in data
    assert "application_id" in data

    # verify assignment did get created
    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, data["application_id"]
    )
    assert len(assignment_user_role_items) == 1
    assert assignment_user_role_items[0].user_role_xref_id == data["user_role_xref_id"]

    # verify assignment linking to correct user
    assignment_user = crud_user.get_user(
        dbPgSession, assignment_user_role_items[0].user_id
    )
    assert assignment_user is not None

    # verify assignment linking to correct role and parent role
    assignment_role = crud_role.get_role(
        dbPgSession, assignment_user_role_items[0].role_id
    )
    assert assignment_role is not None
    assert assignment_role.parent_role_id == TEST_FOM_DEV_SUBMITTER_ROLE_ID

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{data['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204


def test_create_user_role_assignment_with_same_username(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    dbPgSession: Session
):
    # create a user role assignment
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    assignment_one = response.json()

    # allow create a user role assignment with the same username, different role
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_DIFF_ROLE,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    assignment_two = response.json()

    # allow create a user role assignment with the same username, different role
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_DIFF_FCN,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    assignment_three = response.json()

    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, assignment_one["application_id"]
    )
    assert len(assignment_user_role_items) == 3

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{assignment_one['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204

    response = test_client_fixture.delete(
        f"{endPoint}/{assignment_two['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204

    response = test_client_fixture.delete(
        f"{endPoint}/{assignment_three['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204


def test_delete_user_role_assignment(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    dbPgSession: Session
):
    # create a user role assignment
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    data = response.json()
    assert "user_role_xref_id" in data

    # verify assignment did get created
    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, data["application_id"]
    )
    assert len(assignment_user_role_items) == 1
    assert assignment_user_role_items[0].user_role_xref_id == data["user_role_xref_id"]

    # execute Delete
    response = test_client_fixture.delete(
        f"{endPoint}/{data['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204

    # verify user/role assignment has been deleted
    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, data["application_id"]
    )
    assert len(assignment_user_role_items) == 0


def test_assign_same_application_roles_for_different_environments(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    dbPgSession: Session
):
    # create a user role assignment
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_CONCRETE,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    fom_dev_user_role_assignment = response.json()
    assert "user_role_xref_id" in fom_dev_user_role_assignment

    # create a user role assignment with same username and type, but for FOM_TEST role
    access_roles = [FOM_TEST_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=TEST_USER_ROLE_ASSIGNMENT_FOM_TEST_CONCRETE,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
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
    assert fom_test_user_role_assignment["application_id"] \
        == TEST_FOM_TEST_APPLICATION_ID

    # verify assignment did get created for fom_dev
    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, TEST_FOM_DEV_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 1
    assert assignment_user_role_items[0].user_role_xref_id == \
        fom_dev_user_role_assignment["user_role_xref_id"]

    # verify assignment did get created for fom_test
    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, TEST_FOM_TEST_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 1
    assert assignment_user_role_items[0].user_role_xref_id == \
        fom_test_user_role_assignment["user_role_xref_id"]

    # cleanup
    access_roles = [FOM_DEV_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.delete(
        f"{endPoint}/{fom_dev_user_role_assignment['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204

    # verify no user role assignment for fom_dev, but still have one for fom_test
    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, TEST_FOM_DEV_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 0
    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, TEST_FOM_TEST_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 1

    # cleanup
    access_roles = [FOM_TEST_ADMIN_ROLE]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles)
    response = test_client_fixture.delete(
        f"{endPoint}/{fom_test_user_role_assignment['user_role_xref_id']}",
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 204

    # verify no user role assignment for fom_test
    assignment_user_role_items = crud_application.get_application_role_assignments(
        dbPgSession, TEST_FOM_TEST_APPLICATION_ID
    )
    assert len(assignment_user_role_items) == 0
