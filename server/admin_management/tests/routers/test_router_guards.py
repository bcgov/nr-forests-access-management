import pytest
from fastapi import HTTPException, status, Depends
from unittest.mock import MagicMock
from api.app.routers import router_guards
from api.app.services.user_service import UserService

class DummyUserService:
    def get_user_by_cognito_user_id(self, cognito_user_id):
        return None

# Mock FamUser object with required fields for Requester
class MockFamUser:
    def __init__(self):
        self.cognito_user_id = "dummy_id"
        self.user_id = 123
        self.user_guid = "A" * 32
        self.business_guid = None
        self.user_name = "testuser"
        self.first_name = "Test"
        self.last_name = "User"
        self.email = "test@example.com"
        self.user_type_code = "I"  # 'I' for IDIR, 'B' for BCEID

def test_get_current_requester_raises_no_requester_exception():
    # Patch the user_service_instance dependency to return DummyUserService
    with pytest.raises(HTTPException) as exc_info:
        router_guards.get_current_requester(
            request_cognito_user_id="dummy_id",
            access_roles=[],
            user_service=DummyUserService()
        )
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail["code"] == router_guards.ERROR_REQUESTER_NOT_EXISTS


def test_get_current_requester_returns_requester():
    class UserServiceWithUser:
        def get_user_by_cognito_user_id(self, cognito_user_id):
            return MockFamUser()

    access_roles = ["FAM_ADMIN"]
    requester = router_guards.get_current_requester(
        request_cognito_user_id="dummy_id",
        access_roles=access_roles,
        user_service=UserServiceWithUser()
    )
    from api.app.schemas.schemas import Requester
    assert isinstance(requester, Requester)
    assert requester.user_id == 123
    assert requester.user_guid == "A" * 32
    assert requester.user_name == "testuser"
    assert requester.access_roles == access_roles
