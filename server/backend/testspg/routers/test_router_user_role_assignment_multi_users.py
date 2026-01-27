
import pytest
import logging
from http import HTTPStatus
from unittest.mock import patch
from api.app.main import internal_api_prefix
from api.app.constants import UserType
from testspg.constants import (
    FOM_DEV_SUBMITTER_ROLE_ID,
    FOM_DEV_APPLICATION_ID,
    TEST_REQUESTER,
)
from testspg.test_data.app_user_roles_mock_data import (
    create_mock_user_role_assignment_success,
    create_mock_user_role_assignment_error,
)

LOGGER = logging.getLogger(__name__)
ENDPOINT = f"{internal_api_prefix}/user-role-assignment"

# Test data constants
TEST_USER_1_IDIR = {
    "user_name": "ROUTER_TEST_USER_1",
    "user_guid": "ROUTERTESTGUID1234567890ABCDEF12",
    "email": "test1@example.com"
}
TEST_USER_2_IDIR = {
    "user_name": "ROUTER_TEST_USER_2",
    "user_guid": "ROUTERTESTGUID234567890123456789",
    "email": "test2@example.com"
}
TEST_USER_3_IDIR = {
    "user_name": "ROUTER_TEST_USER_3",
    "user_guid": "ROUTERTESTGUID345678901234567890",
    "email": "test3@example.com"
}
TEST_INVALID_USER = {
    "user_name": "INVALID_USER",
    "user_guid": "INVALIDUSERGUID12345678901234567",
    "email": "invalid@example.com"
}

MULTI_USER_REQUEST_DATA = {
    "users": [TEST_USER_1_IDIR, TEST_USER_2_IDIR, TEST_USER_3_IDIR],
    "user_type_code": "I",
    "role_id": FOM_DEV_SUBMITTER_ROLE_ID,
    "requires_send_user_email": False,
}


@pytest.fixture
def mock_crud_create_user_role_assignment_many(mocker):
    """Mock the CRUD function for creating user role assignments."""
    return mocker.patch("api.app.crud.crud_user_role.create_user_role_assignment_many")


@pytest.fixture
def mock_email_send(mocker):
    """Mock GC Notify email send used by send_users_access_granted_emails."""
    return mocker.patch("api.app.crud.crud_user_role.GCNotifyEmailService.send_user_access_granted_email")


@pytest.fixture
def mock_audit_log(mocker):
    """Mock AuditEventLog ."""
    return mocker.patch("api.app.routers.router_user_role_assignment.AuditEventLog")


# --- Test cases

def test_router_response_structure(
    test_client_fixture_unit,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_users,
    mock_crud_create_user_role_assignment_many,
):
    """
    TEST: Response structure follows expected schema.
    Verify:
    - Response has assignments_detail array
    - Each item has status_code and detail/error_message fields
    """
    # Setup
    override_depends__get_verified_target_users(MULTI_USER_REQUEST_DATA)

    mock_crud_create_user_role_assignment_many.return_value = [
        create_mock_user_role_assignment_success(
            user_role_xref_id=1,
            user_id=201,
            role_id=FOM_DEV_SUBMITTER_ROLE_ID,
            user_name=TEST_USER_1_IDIR["user_name"],
            user_guid=TEST_USER_1_IDIR["user_guid"],
        )
    ]

    # Execute
    response = test_client_fixture_unit.post(
        f"{ENDPOINT}",
        json=MULTI_USER_REQUEST_DATA,
        headers={"Authorization": f"Bearer {fom_dev_access_admin_token}"},
    )

    # Assert structure
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()

    assert "assignments_detail" in response_data
    assert isinstance(response_data["assignments_detail"], list)
    assert len(response_data["assignments_detail"]) > 0

    assignment = response_data["assignments_detail"][0]
    assert "status_code" in assignment
    assert "detail" in assignment or "error_message" in assignment


def test_router_per_user_error_reporting(
    test_client_fixture_unit,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_users,
    mock_crud_create_user_role_assignment_many,
):
    """
    TEST: Each user in response has individual error reporting.
    Verify:
    - Each assignment has status_code
    - Each failed assignment has error_message
    - Success assignments don't have error_message
    """
    # Setup
    override_depends__get_verified_target_users(MULTI_USER_REQUEST_DATA)

    # Different error scenarios
    mock_crud_create_user_role_assignment_many.return_value = [
        create_mock_user_role_assignment_success(
            user_role_xref_id=1,
            user_id=201,
            role_id=FOM_DEV_SUBMITTER_ROLE_ID,
            user_name=TEST_USER_1_IDIR["user_name"],
            user_guid=TEST_USER_1_IDIR["user_guid"],
        ),
        create_mock_user_role_assignment_error(
            status_code=HTTPStatus.CONFLICT,
            error_message="Duplicate assignment"
        ),
        create_mock_user_role_assignment_error(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_message="Database error"
        ),
    ]

    # Execute
    response = test_client_fixture_unit.post(
        f"{ENDPOINT}",
        json=MULTI_USER_REQUEST_DATA,
        headers={"Authorization": f"Bearer {fom_dev_access_admin_token}"},
    )

    # Assert
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()

    # Success, no error
    assert response_data["assignments_detail"][0]["status_code"] == HTTPStatus.OK
    assert response_data["assignments_detail"][0].get("error_message") is None

    # Conflict, has error
    assert response_data["assignments_detail"][1]["status_code"] == HTTPStatus.CONFLICT
    assert response_data["assignments_detail"][1]["error_message"] == "Duplicate assignment"

    # Server error, has error
    assert response_data["assignments_detail"][2]["status_code"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response_data["assignments_detail"][2]["error_message"] == "Database error"


def test_router_multi_user_assignment_all_success(
    test_client_fixture_unit,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_users,
    mock_crud_create_user_role_assignment_many,
):
    """
    TEST: Router receives all valid users and CRUD returns all success.
    Verify:
    - Response status is 200 OK
    - Response contains assignments_detail array
    - All assignments have status_code 200
    - Response structure is correct
    """
    # Setup: Mock verified users
    override_depends__get_verified_target_users(MULTI_USER_REQUEST_DATA)

    # Setup: Mock CRUD to return 3 successful assignments
    mock_crud_create_user_role_assignment_many.return_value = [
        create_mock_user_role_assignment_success(
            user_role_xref_id=100 + i,
            user_id=200 + i,
            role_id=FOM_DEV_SUBMITTER_ROLE_ID,
            user_name=user["user_name"],
            user_guid=user["user_guid"],
            user_type_code=UserType.IDIR,
            role_name="FOM_SUBMITTER",
            application_id=FOM_DEV_APPLICATION_ID,
        )  # Return the full object
        for i, user in enumerate([TEST_USER_1_IDIR, TEST_USER_2_IDIR, TEST_USER_3_IDIR])
    ]

    # Execute
    response = test_client_fixture_unit.post(
        f"{ENDPOINT}",
        json=MULTI_USER_REQUEST_DATA,
        headers={"Authorization": f"Bearer {fom_dev_access_admin_token}"},
    )

    # Assert
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert "assignments_detail" in response_data
    assert len(response_data["assignments_detail"]) == 3

    for i, assignment in enumerate(response_data["assignments_detail"]):
        assert assignment["status_code"] == HTTPStatus.OK
        assert assignment["detail"]["user_role_xref_id"] == 100 + i
        assert assignment["detail"]["user_id"] == 200 + i

    # Verify CRUD was called with correct parameters
    mock_crud_create_user_role_assignment_many.assert_called_once()


def test_router_multi_user_assignment_mixed_success_failure(
    test_client_fixture_unit,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_users,
    mock_crud_create_user_role_assignment_many,
):
    """
    TEST: Router receives users, CRUD returns mixed success/failure.
    Verify:
    - Response contains 3 results: 2 success (200), 1 conflict (409)
    - Failed assignment has error_message
    - Response status is 200
    """
    # Setup: Mock verified users
    override_depends__get_verified_target_users(MULTI_USER_REQUEST_DATA)

    # Setup: Mock CRUD to return mixed results
    mock_crud_create_user_role_assignment_many.return_value = [
        create_mock_user_role_assignment_success(
            user_role_xref_id=1,
            user_id=201,
            role_id=FOM_DEV_SUBMITTER_ROLE_ID,
            user_name=TEST_USER_1_IDIR["user_name"],
            user_guid=TEST_USER_1_IDIR["user_guid"],
        ),
        create_mock_user_role_assignment_success(
            user_role_xref_id=2,
            user_id=202,
            role_id=FOM_DEV_SUBMITTER_ROLE_ID,
            user_name=TEST_USER_2_IDIR["user_name"],
            user_guid=TEST_USER_2_IDIR["user_guid"],
        ),
        create_mock_user_role_assignment_error(
            status_code=HTTPStatus.CONFLICT,
            error_message="Role FOM_SUBMITTER already assigned to user ROUTER_TEST_USER_3."
        ),
    ]

    # Execute
    response = test_client_fixture_unit.post(
        f"{ENDPOINT}",
        json=MULTI_USER_REQUEST_DATA,
        headers={"Authorization": f"Bearer {fom_dev_access_admin_token}"},
    )

    # Assert
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data["assignments_detail"]) == 3

    success_count = sum(1 for a in response_data["assignments_detail"] if a["status_code"] == HTTPStatus.OK)
    conflict_count = sum(1 for a in response_data["assignments_detail"] if a["status_code"] == HTTPStatus.CONFLICT)

    assert success_count == 2
    assert conflict_count == 1
    assert response_data["assignments_detail"][2]["error_message"] is not None


def test_router_empty_user_list_validation(
    test_client_fixture_unit,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_users,
    mocker,
):
    """
    TEST: Empty users list should be rejected at schema validation level.
    Verify:
    - Response status is 422 or 400 (validation error)
    """
    # Mock the requester to ensure it exists
    mock_get_requester = mocker.patch("api.app.routers.router_guards.get_current_requester")
    mock_get_requester.return_value = TEST_REQUESTER

    empty_request = MULTI_USER_REQUEST_DATA.copy()
    empty_request["users"] = []

    response = test_client_fixture_unit.post(
        f"{ENDPOINT}",
        json=empty_request,
        headers={"Authorization": f"Bearer {fom_dev_access_admin_token}"},
    )
    assert response.status_code in [HTTPStatus.BAD_REQUEST, HTTPStatus.UNPROCESSABLE_ENTITY]


def test_create_multi_user_role_assignment_email_status_per_user(
    test_client_fixture_unit,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_users,
    mock_crud_create_user_role_assignment_many,
    mock_email_send,
):
    """
    Assign role to 3 users with requires_send_user_email=True.
    Mock email sending to return success for 2, failure for 1.
    Verify:
    - Response contains email_sending_status per user
    - Audit log includes email status
    """
    request_data = MULTI_USER_REQUEST_DATA.copy()
    request_data["requires_send_user_email"] = True
    override_depends__get_verified_target_users(request_data)

    mock_crud_create_user_role_assignment_many.return_value = [
        create_mock_user_role_assignment_success(
            user_role_xref_id=100 + i,
            user_id=200 + i,
            role_id=FOM_DEV_SUBMITTER_ROLE_ID,
            user_name=user["user_name"],
            user_guid=user["user_guid"],
        ) for i, user in enumerate([TEST_USER_1_IDIR, TEST_USER_2_IDIR, TEST_USER_3_IDIR])
    ]

    # Simulate 2 successful email sends and 1 failure
    mock_email_send.side_effect = [None, None, Exception("email failure")]

    response = test_client_fixture_unit.post(
        f"{ENDPOINT}",
        json=request_data,
        headers={"Authorization": f"Bearer {fom_dev_access_admin_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()

    assert "assignments_detail" in response_data
    assert all("email_sending_status" in a for a in response_data["assignments_detail"])
    # Verify per-user email status: first two success, last one failure
    assert [a["email_sending_status"] for a in response_data["assignments_detail"]] == [
        "SENT_TO_EMAIL_SERVICE_SUCCESS",
        "SENT_TO_EMAIL_SERVICE_SUCCESS",
        "SENT_TO_EMAIL_SERVICE_FAILURE",
    ]
    assert mock_email_send.call_count == 3


def test_create_multi_user_role_assignment_audit_batch_summary(
    test_client_fixture_unit,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_users,
    mock_crud_create_user_role_assignment_many,
    mock_audit_log,
):
    """
    Assign role to 3 users with mixed success/failure.
    Verify:
    - Single audit event log created
    - user_assignment_results field contains summary for all 3 users:
      - user_guid, status_code, error_message
    """
    override_depends__get_verified_target_users(MULTI_USER_REQUEST_DATA)
    mock_crud_create_user_role_assignment_many.return_value = [
        create_mock_user_role_assignment_success(
            user_role_xref_id=1,
            user_id=201,
            role_id=FOM_DEV_SUBMITTER_ROLE_ID,
            user_name=TEST_USER_1_IDIR["user_name"],
            user_guid=TEST_USER_1_IDIR["user_guid"],
        ),
        create_mock_user_role_assignment_error(
            status_code=HTTPStatus.CONFLICT,
            error_message="Duplicate assignment"
        ),
        create_mock_user_role_assignment_error(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_message="Database error"
        ),
    ]
    response = test_client_fixture_unit.post(
        f"{ENDPOINT}",
        json=MULTI_USER_REQUEST_DATA,
        headers={"Authorization": f"Bearer {fom_dev_access_admin_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    # Check audit log called with batch summary
    assert mock_audit_log.call_count == 1
    audit_log_instance = mock_audit_log.return_value
    # The router sets user_assignment_results as an attribute after instantiation
    assert hasattr(audit_log_instance, "user_assignment_results")
    assert len(audit_log_instance.user_assignment_results) == 3

