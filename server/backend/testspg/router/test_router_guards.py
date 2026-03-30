from unittest.mock import MagicMock, patch

import pytest
from api.app.constants import UserType
from api.app.models.model import FamUser
from api.app.routers import router_guards
from sqlalchemy import insert
from sqlalchemy.orm import Session
from testspg.constants import TEST_CREATOR, USER_NAME_BCEID_LOAD_2_TEST
from testspg.jwt_utils import COGNITO_USERNAME_BCEID_DELEGATED_ADMIN


def mock_requester(user_name="test_user", user_id=1):
    class DummyRequester:
        def __init__(self):
            self.user_name = user_name
            self.user_id = user_id
    return DummyRequester()

def mock_application(application_id=123, application_name="TestApp"):
    class DummyApplication:
        def __init__(self):
            self.application_id = application_id
            self.application_name = application_name
    return DummyApplication()

## ---

def test_get_current_requester_contains_is_delegated_admin(
    db_pg_session: Session
):
    """
    Test the `get_current_requester` function result:
    * when user is a delegated admin => is_delegated_admin: True
    * when user is not a delegated admin => is_delegated_admin: False
    """
    # as not a delegated admin
    cognito_user_id = "not_delegated_admin_cognito_user_id"
    db_pg_session.execute(
        insert(FamUser),
        [{
            "user_type_code": UserType.BCEID,
            "user_name": USER_NAME_BCEID_LOAD_2_TEST,
            "user_guid": "_test_dummy_user_guid_32_length_",
            "cognito_user_id": cognito_user_id,
            "create_user": TEST_CREATOR,
        }]
    )
    requester = router_guards.get_current_requester(
        request_cognito_user_id=cognito_user_id,
        access_roles=["dummy", "role"],
        db=db_pg_session
    )
    assert requester.user_name == USER_NAME_BCEID_LOAD_2_TEST
    assert requester.is_delegated_admin is False

    # as a delegated admin
    requester = router_guards.get_current_requester(
        request_cognito_user_id=COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
        access_roles=["dummy", "role"],
        db=db_pg_session
    )
    assert requester.cognito_user_id == COGNITO_USERNAME_BCEID_DELEGATED_ADMIN
    assert requester.is_delegated_admin is True


@patch("api.app.crud.crud_application.get_application_by_app_client_id")
@patch("api.app.crud.crud_utils.allow_ext_call_api_permission")
def test_authorize_ext_api_by_app_role_success(mock_allow_permission, mock_get_app):
    test_app_id = 999
    test_app_name = "TestApp"
    mock_get_app.return_value = mock_application(application_id=test_app_id, application_name=test_app_name)
    mock_allow_permission.return_value = True
    requester = mock_requester()
    app_client_id = "valid-client-id"
    db = MagicMock()

    result = router_guards.authorize_ext_api_by_app_role(requester=requester, app_client_id=app_client_id, db=db)
    assert result.application_id == test_app_id
    assert result.application_name == test_app_name

@patch("api.app.crud.crud_application.get_application_by_app_client_id")
@patch("api.app.crud.crud_utils.allow_ext_call_api_permission")
def test_authorize_ext_api_by_app_role_invalid_app_client_id(mock_allow_permission, mock_get_app):
    mock_get_app.return_value = None
    mock_allow_permission.return_value = False
    requester = mock_requester()
    app_client_id = "invalid-client-id"
    db = MagicMock()

    with pytest.raises(Exception) as excinfo:
        router_guards.authorize_ext_api_by_app_role(requester=requester, app_client_id=app_client_id, db=db)
    assert "invalid application client id" in str(excinfo.value)

@patch("api.app.crud.crud_application.get_application_by_app_client_id")
@patch("api.app.crud.crud_utils.allow_ext_call_api_permission")
def test_authorize_ext_api_by_app_role_no_permission(mock_allow_permission, mock_get_app):
    mock_get_app.return_value = mock_application()
    mock_allow_permission.return_value = False
    requester = mock_requester()
    app_client_id = "valid-client-id"
    db = MagicMock()

    with pytest.raises(Exception) as excinfo:
        router_guards.authorize_ext_api_by_app_role(requester=requester, app_client_id=app_client_id, db=db)
    assert "No permission to call the external API" in str(excinfo.value)

# ---
# Tests for enforce_bceid_by_same_org_guard

@pytest.mark.asyncio
async def test_enforce_bceid_by_same_org_guard_idir_requester():
    """
    Test enforce_bceid_by_same_org_guard: IDIR requester, should not call validation, should not raise.
    """
    requester = MagicMock()
    requester.user_type_code = router_guards.UserType.IDIR
    role = MagicMock()
    role.application = MagicMock()
    role.application.application_name = "TestApp"

    # Should not raise, should not call validate_target_users or validate_bceid_same_org
    try:
        await router_guards.enforce_bceid_by_same_org_guard(
            _enforce_fam_access_validated=None,
            _enforce_user_type_auth=None,
            requester=requester,
            target_users=[MagicMock()],
            role=role,
        )
    except Exception:
        pytest.fail("Should not raise for IDIR requester")


@pytest.mark.asyncio
@patch("api.app.routers.router_guards.validate_bceid_same_org")
@patch("api.app.routers.router_guards.validate_target_users")
async def test_enforce_bceid_by_same_org_guard_success(mock_validate_target_users, mock_validate_same_org):
    """
    Test enforce_bceid_by_same_org_guard: BCeID requester, all target users verified, same org, no error.
    """
    # Setup requester (BCeID)
    requester = MagicMock()
    requester.user_type_code = router_guards.UserType.BCEID
    requester.user_name = "bceid_user"

    # Setup role
    role = MagicMock()
    role.application = MagicMock()
    role.application.application_name = "TestApp"

    # Setup validation result: all users verified, none failed
    validation_result = MagicMock()
    validation_result.failed_users = []
    validation_result.verified_users = [MagicMock(user_name="target1"), MagicMock(user_name="target2")]
    mock_validate_target_users.return_value = validation_result

    # Should not raise
    try:
        await router_guards.enforce_bceid_by_same_org_guard(
            _enforce_fam_access_validated=None,
            _enforce_user_type_auth=None,
            requester=requester,
            target_users=[MagicMock()],
            role=role,
        )
    except Exception:
        pytest.fail("Should not raise when all users verified and same org")
    # Verify organization validation was called
    assert mock_validate_same_org.call_count == 1


@pytest.mark.asyncio
@patch("api.app.routers.router_guards.validate_bceid_same_org")
@patch("api.app.routers.router_guards.validate_target_users")
async def test_enforce_bceid_by_same_org_guard_failed_users(mock_validate_same_org, mock_validate_target_users):
    """
    Test enforce_bceid_by_same_org_guard: BCeID requester, some target users failed verification.
    """
    requester = MagicMock()
    requester.user_type_code = router_guards.UserType.BCEID
    role = MagicMock()
    role.application = MagicMock()
    role.application.application_name = "TestApp"

    failed_user = MagicMock(user_name="failed_user")
    validation_result = MagicMock()
    validation_result.failed_users = [failed_user]
    validation_result.verified_users = []
    mock_validate_target_users.return_value = validation_result

    with pytest.raises(Exception) as excinfo:
        await router_guards.enforce_bceid_by_same_org_guard(
            _enforce_fam_access_validated=None,
            _enforce_user_type_auth=None,
            requester=requester,
            target_users=[MagicMock()],
            role=role,
        )
    assert "Unable to verify the following users" in str(excinfo.value)


@pytest.mark.asyncio
@patch("api.app.routers.router_guards.validate_bceid_same_org")
@patch("api.app.routers.router_guards.validate_target_users")
async def test_enforce_bceid_by_same_org_guard_diff_org_error(mock_validate_target_users, mock_validate_same_org, patch_raise_http_exception):
    """
    Test enforce_bceid_by_same_org_guard: BCeID requester, all users verified, but org validation fails.
    """
    requester = MagicMock()
    requester.user_type_code = router_guards.UserType.BCEID
    role = MagicMock()
    role.application = MagicMock()
    role.application.application_name = "TestApp"

    validation_result = MagicMock()
    validation_result.failed_users = []
    validation_result.verified_users = [MagicMock(user_name="target1")]
    mock_validate_target_users.return_value = validation_result
    mock_validate_same_org.side_effect = Exception("Different org error")

    with pytest.raises(Exception) as excinfo:
        await router_guards.enforce_bceid_by_same_org_guard(
            _enforce_fam_access_validated=None,
            _enforce_user_type_auth=None,
            requester=requester,
            target_users=[MagicMock()],
            role=role,
        )
    assert "An error occurred while validating organization consistency" in str(excinfo.value)


# --- Tests for get_target_users_from_ids

@pytest.mark.asyncio
@patch("api.app.schemas.TargetUserSchema.model_validate")
@patch("api.app.crud.crud_user_role.find_by_id")
async def test_get_target_users_from_ids_path_param_valid_user_role_xref_id(mock_find_by_id, mock_model_validate):
    """
    Test get_target_users_from_ids with valid user_role_xref_id in path params.
    Should return a list containing one TargetUserSchema.
    """
    user_role_xref_id = 123
    user_name = "test_user"
    user_type_code = UserType.BCEID
    user_guid = "12345678901234567890123456789abc"

    # Setup mock user role and user
    mock_user = MagicMock()
    mock_find_by_id.return_value = MagicMock(user=mock_user)

    # Mock TargetUserSchema.model_validate to return a valid TargetUserSchema object
    mock_target_user = MagicMock()
    mock_target_user.user_name = user_name
    mock_target_user.user_type_code = user_type_code
    mock_target_user.user_guid = user_guid
    mock_model_validate.return_value = mock_target_user

    # Setup request with user_role_xref_id in path_params
    mock_request = MagicMock()
    mock_request.path_params = {"user_role_xref_id": user_role_xref_id}

    # Setup database dependency
    mock_db = MagicMock()

    # Call the function
    result = await router_guards.get_target_users_from_ids(
        request=mock_request,
        db=mock_db
    )

    # Assertions
    assert len(result) == 1
    assert result[0].user_name == user_name
    assert result[0].user_type_code == user_type_code
    assert result[0].user_guid == user_guid
    mock_find_by_id.assert_called_once_with(mock_db, user_role_xref_id)
    mock_model_validate.assert_called_once_with(mock_user)


@pytest.mark.asyncio
@patch("api.app.crud.crud_user_role.find_by_id")
async def test_get_target_users_from_ids_path_param_invalid_user_role_xref_id(mock_find_by_id):
    """
    Test get_target_users_from_ids with invalid user_role_xref_id in path params.
    Should raise HTTP exception when user role is not found.
    """
    mock_find_by_id.return_value = None

    # Setup request with user_role_xref_id in path_params
    mock_request = MagicMock()
    mock_request.path_params = {"user_role_xref_id": 999}

    # Setup database dependency
    mock_db = MagicMock()

    # Call the function and expect exception
    with pytest.raises(Exception) as excinfo:
        await router_guards.get_target_users_from_ids(
            request=mock_request,
            db=mock_db
        )

    assert "Parameter 'user_role_xref_id' is missing or invalid" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_target_users_from_ids_body_single_user():
    """
    Test get_target_users_from_ids with single user dict in request body.
    Should return a list containing one TargetUserSchema.
    """
    # Setup request with single user in body
    mock_request = MagicMock()
    mock_request.path_params = {}

    user_name = "single_user"
    user_type_code = UserType.IDIR
    user_guid = "single-user-guid-abcd1234567890e"

    # Mock json() to return an awaitable
    async def mock_json():
        return {
            "users": [
                {
                    "user_name": user_name,
                    "user_guid": user_guid
                }
            ],
            "user_type_code": user_type_code,
        }
    mock_request.json = mock_json

    # Setup database dependency
    mock_db = MagicMock()

    # Call the function
    result = await router_guards.get_target_users_from_ids(
        request=mock_request,
        db=mock_db
    )

    # Assertions
    assert len(result) == 1
    assert result[0].user_name == user_name
    assert result[0].user_type_code == UserType.IDIR
    assert result[0].user_guid == user_guid


@pytest.mark.asyncio
async def test_get_target_users_from_ids_body_multiple_users():
    """
    Test get_target_users_from_ids with multiple users in request body via 'users' key.
    Should return a list containing multiple TargetUserSchema objects.
    """
    # Setup request with multiple users in body
    mock_request = MagicMock()
    mock_request.path_params = {}

    # Define reusable variables
    user_type_code = UserType.BCEID
    users = [
        {
            "user_name": "user1",
            "user_guid": "user1guid-abcd1234567890ef123456"
        },
        {
            "user_name": "user2",
            "user_guid": "user2guid-abcd1234567890ef123456"
        }
    ]

    # Mock json() to return an awaitable
    async def mock_json():
        return {
            "user_type_code": user_type_code,
            "users": users
        }
    mock_request.json = mock_json

    # Setup database dependency
    mock_db = MagicMock()

    # Call the function
    result = await router_guards.get_target_users_from_ids(
        request=mock_request,
        db=mock_db
    )

    # Assertions
    assert len(result) == 2
    assert result[0].user_name == users[0]["user_name"]
    assert result[0].user_type_code == UserType.BCEID
    assert result[0].user_guid == users[0]["user_guid"]
    assert result[1].user_name == users[1]["user_name"]
    assert result[1].user_type_code == UserType.BCEID
    assert result[1].user_guid == users[1]["user_guid"]


@pytest.mark.asyncio
async def test_get_target_users_from_ids_body_missing_required_field():
    """
    Test get_target_users_from_ids when required field is missing from user dict.
    Should raise an exception when user_name or user_guid is missing.
    """
    # Setup request with missing user_guid field
    mock_request = MagicMock()
    mock_request.path_params = {}

    # Mock json() to return an awaitable
    async def mock_json():
        return {
            "users": [
                {
                    # missing user_guid
                    "user_name": "incomplete_user"
                }
            ],
            "user_type_code": UserType.IDIR

        }
    mock_request.json = mock_json

    # Setup database dependency
    mock_db = MagicMock()

    # Call the function and expect exception
    with pytest.raises(Exception):
        await router_guards.get_target_users_from_ids(
            request=mock_request,
            db=mock_db
        )


@pytest.mark.asyncio
async def test_get_target_users_from_ids_body_missing_user_type_code():
    """
    Test get_target_users_from_ids when user_type_code is missing from body.
    Should raise an exception when user_type_code is missing in request body.
    """
    # Setup request missing user_type_code
    mock_request = MagicMock()
    mock_request.path_params = {}

    # Mock json() to return an awaitable
    async def mock_json():
        return {
            "users": [
                {
                    "user_guid": "user-guid-abcd1234567890ef1234567890e",
                    "user_name": "user_no_type",
                }
            ],
            # missing user_type_code
        }
    mock_request.json = mock_json

    # Setup database dependency
    mock_db = MagicMock()

    # Call the function and expect exception
    with pytest.raises(Exception):
        await router_guards.get_target_users_from_ids(
            request=mock_request,
            db=mock_db
        )


@pytest.mark.asyncio
async def test_get_target_users_from_ids_body_empty_users_list():
    """
    Test get_target_users_from_ids with empty 'users' list in request body.
    Should raise an exception when no users are provided.
    """
    # Setup request with empty users list
    mock_request = MagicMock()
    mock_request.path_params = {}

    # Mock json() to return an awaitable
    async def mock_json():
        return {
            "users": []  # Explicitly set an empty list for users
        }
    mock_request.json = mock_json

    # Setup database dependency
    mock_db = MagicMock()

    # Call the function and expect exception
    with pytest.raises(Exception) as excinfo:
        await router_guards.get_target_users_from_ids(
            request=mock_request,
            db=mock_db
        )

    assert "The 'users' list in the request body is empty or missing." in str(excinfo.value)
