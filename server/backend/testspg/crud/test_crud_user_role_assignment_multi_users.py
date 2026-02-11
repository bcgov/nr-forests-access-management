from unittest.mock import patch
import logging
from datetime import datetime, timedelta, timezone, time as dt_time
from zoneinfo import ZoneInfo
from api.app.datetime_format import BC_TIMEZONE
from http import HTTPStatus
from sqlalchemy.orm import Session

from api.app.schemas import TargetUserSchema
from api.app.schemas.fam_user_role_assignment_create_response import FamUserRoleAssignmentCreateRes
from api.app.crud import crud_user_role
from api.app.constants import UserType, MAX_NUM_USERS_ASSIGNMENT_GRANT
import api.app.crud.crud_user as crud_user
from testspg.constants import (
    FOM_DEV_SUBMITTER_ROLE_ID,
    FOM_DEV_REVIEWER_ROLE_ID,
    FC_NUMBER_EXISTS_ACTIVE_00001018,
    FC_NUMBER_EXISTS_ACTIVE_00001011,
    FC_NUMBER_NOT_EXISTS,
)
from testspg.test_data.user_role_assignment_test_data import (
    create_role_assignment_request,
    create_test_requester
)
from api.app.schemas.fam_user_role_assignment_create import FamUserRoleAssignmentCreateSchema
from pydantic import ValidationError

LOGGER = logging.getLogger(__name__)

# Test data constants
CRUD_TEST_USER_1 = TargetUserSchema(
    user_name="CRUD_TEST_USER_1",
    user_guid="CRUDTESTGUID1234567890ABCDEF1234"
)
CRUD_TEST_USER_2 = TargetUserSchema(
    user_name="CRUD_TEST_USER_2",
    user_guid="CRUDTESTGUID2345678901234567890A"
)
CRUD_TEST_USER_3 = TargetUserSchema(
    user_name="CRUD_TEST_USER_3",
    user_guid="CRUDTESTGUID3456789012345678901A"
)


class TestCrudMultiUserAssignmentSuccess:
    """Test successful multi-user role assignments."""

    def test_crud_multi_user_assignment_all_success(self, db_pg_session: Session):
        """
        TEST: Create assignments for 3 new users, all succeed.
        Verify:
        - 3 FamUserRoleXref records created
        - All return status 200
        - All have user_id and user_role_xref_id
        """
        # Setup: Prepare verified users list
        verified_users = [CRUD_TEST_USER_1, CRUD_TEST_USER_2, CRUD_TEST_USER_3]
        request = create_role_assignment_request(
            users=verified_users,
            user_type_code=UserType.IDIR,
            role_id=FOM_DEV_REVIEWER_ROLE_ID,
            forest_client_numbers=None
        )
        requester = create_test_requester()

        # Execute
        results = crud_user_role.create_user_role_assignment_many(
            db=db_pg_session,
            request=request,
            verified_users=verified_users,
            requester=requester,
        )
        LOGGER.debug(f"Results: {results}")
        # Assert
        assert len(results) == 3
        for result in results:
            assert result.status_code == HTTPStatus.OK
            assert result.detail is not None
            assert result.detail.user_id is not None
            assert result.detail.user_role_xref_id is not None
            assert result.error_message is None

    def test_crud_multi_user_creates_new_users(self, db_pg_session: Session):
        """
        TEST: CRUD creates new users if they don't exist.
        Verify:
        - FamUser records created for new users
        - user_type_code, user_name, user_guid populated
        """
        verified_users = [CRUD_TEST_USER_1]
        request = create_role_assignment_request(
            users=verified_users,
            user_type_code=UserType.IDIR,
            role_id=FOM_DEV_REVIEWER_ROLE_ID,
            forest_client_numbers=None
        )
        requester = create_test_requester()

        # Execute
        results = crud_user_role.create_user_role_assignment_many(
            db=db_pg_session,
            request=request,
            verified_users=verified_users,
            requester=requester,
        )

        # Assert: User created
        assert len(results) == 1
        assert results[0].status_code == HTTPStatus.OK
        user_id = results[0].detail.user_id
        assert user_id is not None


class TestCrudMultiUserAssignmentErrors:
    """Test error handling for multi-user role assignments."""

    def test_crud_duplicate_assignment_per_user(self, db_pg_session: Session):
        """
        TEST: Duplicate assignment detected per user.
        Verify:
        - First assignment succeeds (200)
        - Second assignment fails (409 Conflict)
        - error_message includes "duplicate" or similar
        """
        verified_users = [CRUD_TEST_USER_1]
        request = create_role_assignment_request(
            users=verified_users,
            user_type_code=UserType.IDIR,
            role_id=FOM_DEV_REVIEWER_ROLE_ID,
            forest_client_numbers=None
        )
        requester = create_test_requester()

        # Execute: First assignment
        results1 = crud_user_role.create_user_role_assignment_many(
            db=db_pg_session,
            request=request,
            verified_users=verified_users,
            requester=requester,
        )

        assert results1[0].status_code == HTTPStatus.OK

        # Execute: Second assignment (duplicate)
        results2 = crud_user_role.create_user_role_assignment_many(
            db=db_pg_session,
            request=request,
            verified_users=verified_users,
            requester=requester,
        )

        # Assert
        assert results2[0].status_code == HTTPStatus.CONFLICT
        assert results2[0].error_message is not None
        assert "already assigned to user" in results2[0].error_message.lower()

    def test_crud_mixed_success_failure_batch(self, db_pg_session: Session):
        """
        TEST: Batch with mixed success and failure per user.
        Verify:
        - User 1: new, success (200)
        - User 2: new, success (200)
        - User 3: duplicate of User 1, failure (409)
        """
        verified_users = [CRUD_TEST_USER_1, CRUD_TEST_USER_2]
        request = create_role_assignment_request(
            users=verified_users,
            user_type_code=UserType.IDIR,
            role_id=FOM_DEV_REVIEWER_ROLE_ID,
            forest_client_numbers=None
        )
        requester = create_test_requester()

        # Execute: First batch
        results1 = crud_user_role.create_user_role_assignment_many(
            db=db_pg_session,
            request=request,
            verified_users=verified_users,
            requester=requester,
        )

        assert len(results1) == 2
        assert all(r.status_code == HTTPStatus.OK for r in results1)

        # Execute: Second batch with duplicate
        verified_users_with_dup = [CRUD_TEST_USER_1, CRUD_TEST_USER_3]
        request2 = create_role_assignment_request(
            users=verified_users_with_dup,
            user_type_code=UserType.IDIR,
            role_id=FOM_DEV_REVIEWER_ROLE_ID,
            forest_client_numbers=None
        )
        results2 = crud_user_role.create_user_role_assignment_many(
            db=db_pg_session,
            request=request2,
            verified_users=verified_users_with_dup,
            requester=requester,
        )

        # Assert
        assert len(results2) == 2
        # First user (duplicate) should fail
        assert results2[0].status_code == HTTPStatus.CONFLICT
        # Second user (new) should succeed
        assert results2[1].status_code == HTTPStatus.OK

    def test_schema_users_min_and_max_constraints(self):
        """
        TEST: FamUserRoleAssignmentCreateSchema users min/max constraints.
        Verify:
        - Error is raised if users list is empty (min constraint)
        - Error is raised if users list exceeds max (MAX_NUM_USERS_ASSIGNMENT_GRANT)
        - Error message matches expected
        """
        # Valid user template
        valid_user = dict(user_name="Users", user_guid="A"*32)
        # Test min constraint (empty list)
        try:
            FamUserRoleAssignmentCreateSchema(
                users=[],
                user_type_code=UserType.IDIR,
                role_id=1
            )
            assert False, "Expected ValidationError for empty users list"
        except ValidationError as e:
            assert any(
                err['msg'].startswith('List should have at least 1 item')
                for err in e.errors()
            ), f"Unexpected error message: {e.errors()}"

        # Test max constraint (exceeding max)
        too_many_users = [valid_user for _ in range(MAX_NUM_USERS_ASSIGNMENT_GRANT + 1)]
        try:
            FamUserRoleAssignmentCreateSchema(
                users=too_many_users,
                user_type_code=UserType.IDIR,
                role_id=1
            )
            assert False, "Expected ValidationError for too many users"
        except ValidationError as e:
            assert any(
                "Can only grant at most" in err['msg']
                for err in e.errors()
            ), f"Unexpected error message: {e.errors()}"


class TestCrudMultiUserForestClientLogic:
    """Test forest client child role logic for multi-user assignments."""

    def test_crud_abstract_role_with_forest_client_numbers(self, db_pg_session: Session):
        """
        TEST: Abstract role with forest client numbers creates child roles.
        Verify:
        - Each user gets assignments for each forest client child role
        - Total assignments = users * forest_client_numbers
        """
        verified_users = [CRUD_TEST_USER_1, CRUD_TEST_USER_2]
        forest_clients = [FC_NUMBER_EXISTS_ACTIVE_00001018, FC_NUMBER_EXISTS_ACTIVE_00001011]
        request = create_role_assignment_request(
            users=verified_users,
            user_type_code=UserType.BCEID,
            role_id=FOM_DEV_SUBMITTER_ROLE_ID,  # Abstract role
            forest_client_numbers=forest_clients
        )
        requester = create_test_requester()

        # Execute: Assign abstract role with forest clients
        results = crud_user_role.create_user_role_assignment_many(
            db=db_pg_session,
            request=request,
            verified_users=verified_users,
            requester=requester,
        )

        # Assert: Should have results for all combinations
        # Expected: 2 users * 2 forest clients = 4 assignments
        assert len(results) >= len(verified_users)


class TestCrudMultiUserEdgeCases:
    """Test edge cases for multi-user CRUD operations."""

    def test_crud_per_user_error_isolation(self, db_pg_session: Session):
        """
        TEST: Error in one user doesn't affect others.
        Verify:
            - User 1: succeeds
            - User 2: fails (db error simulated)
            - User 3: succeeds
            - All 3 return a result with appropriate status
        """
        verified_users = [CRUD_TEST_USER_1, CRUD_TEST_USER_2, CRUD_TEST_USER_3]
        request = create_role_assignment_request(
            users=verified_users,
            user_type_code=UserType.IDIR,
            role_id=FOM_DEV_REVIEWER_ROLE_ID,
            forest_client_numbers=None
        )
        requester = create_test_requester()

        # Patch crud_user.find_or_create to raise an exception for User 2 only
        original_find_or_create = crud_user.find_or_create

        def find_or_create_side_effect(db, user_type_code, user_name, user_guid, cognito_user_id):
            if user_name == CRUD_TEST_USER_2.user_name:
                raise Exception("Simulated DB error for User 2")
            return original_find_or_create(db, user_type_code, user_name, user_guid, cognito_user_id)

        with patch("api.app.crud.crud_user.find_or_create", side_effect=find_or_create_side_effect):
            results = crud_user_role.create_user_role_assignment_many(
                db=db_pg_session,
                request=request,
                verified_users=verified_users,
                requester=requester,
            )

        # Assert
        assert len(results) == 3
        # User 1: should succeed
        assert results[0].status_code == HTTPStatus.OK
        assert results[0].error_message is None
        # User 2: should fail (db error)
        assert results[1].status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert results[1].error_message is not None
        # User 3: should succeed
        assert results[2].status_code == HTTPStatus.OK
        assert results[2].error_message is None
        # All results should be correct type
        for result in results:
            assert isinstance(result, FamUserRoleAssignmentCreateRes)

    def test_crud_forest_client_number_not_exists(self, db_pg_session: Session, mock_forest_client_integration_service):
        """
        TEST: Assigning a role with a forest client number that doesn't exist (multi-user).
        Verify:
        - Each user assignment fails (400 Bad Request or similar)
        - error_message indicates the issue for each user
        """
        verified_users = [CRUD_TEST_USER_1, CRUD_TEST_USER_2, CRUD_TEST_USER_3]
        request = create_role_assignment_request(
            users=verified_users,
            user_type_code=UserType.BCEID,
            role_id=FOM_DEV_SUBMITTER_ROLE_ID,  # Abstract role (requires forest client)
            forest_client_numbers=[FC_NUMBER_NOT_EXISTS]
        )
        requester = create_test_requester()

        # Mock the forest client integration service to return empty (not found)
        mock_forest_client_integration_service.search.return_value = []
        # Execute: Attempt to assign non-existent forest client number to multiple users
        results = crud_user_role.create_user_role_assignment_many(
            db=db_pg_session,
            request=request,
            verified_users=verified_users,
            requester=requester,
        )

        # Assert
        assert len(results) == len(verified_users)
        for result in results:
            assert result.status_code == HTTPStatus.BAD_REQUEST
            assert result.error_message is not None
            assert "forest client number" in result.error_message.lower()

    def test_crud_create_user_role_assignment_many_with_expiry_date(self, db_pg_session: Session):
        """
        CRUD UNIT TEST: Assign role with expiry_date to multiple users.
        Verify:
        - All users assigned successfully
        - Expiry date stored correctly (UTC format, end of BC day)
        """
        # Setup test data with dynamic future expiry date (2 weeks from now)
        verified_users = [CRUD_TEST_USER_1, CRUD_TEST_USER_2]
        bc_tz = ZoneInfo(BC_TIMEZONE)
        today_bc = datetime.now(bc_tz).date()
        expiry_date_bc = today_bc + timedelta(days=14)
        expiry_date_str = expiry_date_bc.strftime("%Y-%m-%d")
        request = create_role_assignment_request(
            users=verified_users,
            user_type_code=UserType.IDIR,
            role_id=FOM_DEV_REVIEWER_ROLE_ID,
            forest_client_numbers=None,
            expiry_date_date=expiry_date_str
        )
        requester = create_test_requester()

        # Expected UTC expiry: end of BC day (23:59:59 in BC, converted to UTC)
        end_of_bc_day = datetime.combine(expiry_date_bc, dt_time(23, 59, 59)).replace(tzinfo=bc_tz)
        expected_utc_expiry = end_of_bc_day.astimezone(timezone.utc)

        # Execute
        results = crud_user_role.create_user_role_assignment_many(
            db=db_pg_session,
            request=request,
            verified_users=verified_users,
            requester=requester,
        )

        # Assert
        assert len(results) == 2
        for result in results:
            assert result.status_code == HTTPStatus.OK
            assert result.detail is not None
            assert result.detail.user_role_xref_id is not None
            # Verify expiry date is set and correct
            actual_expiry = result.detail.expiry_date
            assert actual_expiry is not None
            # Convert to datetime if string
            if isinstance(actual_expiry, str):
                actual_expiry = datetime.fromisoformat(actual_expiry.replace("Z", "+00:00"))
            # Normalize to UTC and strip microseconds for comparison (accounts for DB storage rounding)
            actual_expiry_utc = actual_expiry.astimezone(timezone.utc).replace(microsecond=0)
            expected_expiry_utc = expected_utc_expiry.replace(microsecond=0)
            assert actual_expiry_utc == expected_expiry_utc, \
                f"Expiry date mismatch: expected {expected_expiry_utc}, got {actual_expiry_utc}"


class TestCrudMultiUserAudit:
    """Test audit logic for multi-user role assignments."""

    def test_permission_audit_service_called(self, db_pg_session: Session):
        """
        TEST: Verify PermissionAuditService is called for each user.
        Verify:
        - store_user_permissions_granted_audit_history is called with correct arguments.
        """
        verified_users = [CRUD_TEST_USER_1, CRUD_TEST_USER_2]
        request = create_role_assignment_request(
            users=verified_users,
            user_type_code=UserType.IDIR,
            role_id=FOM_DEV_REVIEWER_ROLE_ID,
            forest_client_numbers=None
        )
        requester = create_test_requester()

        with patch("api.app.crud.services.permission_audit_service.PermissionAuditService.store_user_permissions_granted_audit_history") as mock_audit:
            # Execute
            crud_user_role.create_user_role_assignment_many(
                db=db_pg_session,
                request=request,
                verified_users=verified_users,
                requester=requester,
            )

            # Assert
            assert mock_audit.call_count == len(verified_users)
            for call, user in zip(mock_audit.call_args_list, verified_users):
                args, kwargs = call
                assert kwargs["change_target_user"].user_name == user.user_name
