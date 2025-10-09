import math
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from api.app.constants import (ERROR_CODE_INVALID_OPERATION, EXT_MIN_PAGE,
                               EXT_MIN_PAGE_SIZE)
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

def test_search_users_permission_denied(mocker, db_pg_session):
    #  Patch is_request_allowed to return False
    mocker.patch.object(ExtAppUserSearchService, "is_request_allowed", return_value=False)
    requester = MagicMock()
    service = ExtAppUserSearchService(db_pg_session, requester=requester, application_id=123)
    page_params = MagicMock()
    filter_params = MagicMock()

    # Act & Assert: Expect raise_http_exception to be called
    with pytest.raises(Exception) as exc_info:
        service.search_users(page_params, filter_params)
    # Check exception message and status code
    assert ERROR_CODE_INVALID_OPERATION in str(exc_info.value)
    assert str(HTTPStatus.INTERNAL_SERVER_ERROR) in str(exc_info.value)


def test_search_users_page_and_size_defaults(mocker, db_pg_session):
    mocker.patch.object(ExtAppUserSearchService, "is_request_allowed", return_value=True)

    # Patch db.execute to return mocked total count
    mock_execute = MagicMock()
    mock_execute.scalar.return_value = 15
    mocker.patch.object(db_pg_session, "execute", return_value=mock_execute)

    mocker.patch.object(ExtAppUserSearchService, "_build_user_search_results", return_value=[]) # dummy, not testing this

    # Patch _apply_user_filters to return a dummy select
    mocker.patch.object(ExtAppUserSearchService, "_apply_user_filters", side_effect=lambda stmt, params: stmt)

    # Patch joinedload and other SQLAlchemy methods to avoid actual DB calls
    mocker.patch("sqlalchemy.orm.joinedload", lambda *a, **kw: None)

    # Prepare params with None for page and size
    page_params = MagicMock()
    page_params.page = None  # no page value at params
    page_params.size = None  # no page size at params
    filter_params = MagicMock()

    service = ExtAppUserSearchService(db_pg_session, requester=MagicMock(), application_id=123)
    result = service.search_users(page_params, filter_params)

    # EXT_MIN_PAGE and EXT_MIN_PAGE_SIZE are imported from constants
    expected_page_count = math.ceil(15 / EXT_MIN_PAGE_SIZE)

    assert result.meta.total== 15
    assert result.meta.page_count == expected_page_count
    assert result.meta.page == EXT_MIN_PAGE
    assert result.meta.size == EXT_MIN_PAGE_SIZE
    assert result.users == []


@pytest.mark.parametrize(
    "total,size,expected_page_count",
    [
        (0, EXT_MIN_PAGE_SIZE, 0),      # No users, page count should be 0
        (1, EXT_MIN_PAGE_SIZE, 1),      # 1 user, page size 10, page count 1
        (10, EXT_MIN_PAGE_SIZE, 1),     # 10 users, page size 10, page count 1
        (11, EXT_MIN_PAGE_SIZE, 2),     # 11 users, page size 10, page count 2
        (20, EXT_MIN_PAGE_SIZE, 2),     # 20 users, page size 10, page count 2
        (21, EXT_MIN_PAGE_SIZE, 3),     # 21 users, page size 10, page count 3
        (25, 12, 3),                    # 25 users, page size 12, page count 3
        (100, 25, 4),                   # 100 users, page size 25, page count 4
    ]
)
def test_search_users_page_count_calculation(mocker, db_pg_session, total, size, expected_page_count):
    # Patch is_request_allowed to return True
    mocker.patch.object(ExtAppUserSearchService, "is_request_allowed", return_value=True)

    # Patch db.execute to return mocked total count
    mock_execute = MagicMock()
    mock_execute.scalar.return_value = total
    mocker.patch.object(db_pg_session, "execute", return_value=mock_execute)

    # Patch _build_user_search_results to return empty list
    mocker.patch.object(ExtAppUserSearchService, "_build_user_search_results", return_value=[]) # dummy, not testing this

    # Patch _apply_user_filters to return a dummy select
    mocker.patch.object(ExtAppUserSearchService, "_apply_user_filters", side_effect=lambda stmt, params: stmt)

    # Patch joinedload and other SQLAlchemy methods to avoid actual DB calls
    mocker.patch("sqlalchemy.orm.joinedload", lambda *a, **kw: None)

    # Prepare params
    page_params = MagicMock()
    page_params.page = 1
    page_params.size = size
    filter_params = MagicMock()

    service = ExtAppUserSearchService(db_pg_session, requester=MagicMock(), application_id=123)
    result = service.search_users(page_params, filter_params)

    assert result.meta.total == total
    assert result.meta.page_count == expected_page_count
    assert result.meta.page == 1
    assert result.meta.size == size
    assert result.users == []

