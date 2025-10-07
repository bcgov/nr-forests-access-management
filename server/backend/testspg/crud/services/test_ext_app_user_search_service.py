from unittest.mock import MagicMock

from api.app.crud.services.ext_app_user_search_service import \
    ExtAppUserSearchService


# -- Tests interface function: is_request_allowed.
def test_is_request_allowed_true(mocker, db_pg_session):
    # Mock allow_ext_call_api_permission to return True
    mocker.patch("api.app.crud.crud_utils.allow_ext_call_api_permission", return_value=True)
    requester = MagicMock()
    service = ExtAppUserSearchService(db_pg_session, requester=requester, application_id=123)
    assert service.is_request_allowed() is True

def test_is_request_allowed_false(mocker, db_pg_session):
    # Mock allow_ext_call_api_permission to return False
    mocker.patch("api.app.crud.crud_utils.allow_ext_call_api_permission", return_value=False)
    requester = MagicMock()
    service = ExtAppUserSearchService(db_pg_session, requester=requester, application_id=123)
    assert service.is_request_allowed() is False

# -- Tests search_users function.