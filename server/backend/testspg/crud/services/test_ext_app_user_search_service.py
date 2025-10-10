import math
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from api.app.constants import (ERROR_CODE_INVALID_OPERATION,
                               ERROR_CODE_INVALID_REQUEST_PARAMETER,
                               EXT_MIN_PAGE, EXT_MIN_PAGE_SIZE, IDPType,
                               UserType)
from api.app.crud.services.ext_app_user_search_service import \
    ExtAppUserSearchService
from api.app.schemas.ext.pagination import ExtUserSearchParamSchema
from api.app.schemas.ext.user_search import ExtApplicationUserSearchSchema
from testspg.constants import FOM_DEV_APPLICATION_ID
from testspg.utils import create_role, create_user


# Dynamically generate mock users for this test case
def make_fam_mock_user(idx):
    user = MagicMock()
    user.first_name = f"First{idx}"
    user.last_name = f"Last{idx}"
    user.user_name = f"user{idx}"
    user.user_guid = f"GUID{idx}"
    user.user_type_code = "IDIR" if idx % 2 == 0 else "BCEID"
    user.fam_user_role_xref = []
    return user
class DummyRequester:
    user_name = "test_user"

@pytest.fixture()
def allow_api_request(mocker):
    mocker.patch.object(ExtAppUserSearchService, "is_request_allowed", return_value=True)


@pytest.fixture(scope="function")
def setup_users_and_roles_for_ext_user_search_tests(db_pg_session):
    # Use FOM_DEV_APPLICATION_ID for application_id
    app_id = FOM_DEV_APPLICATION_ID

    # Create roles
    role_admin = create_role(db_pg_session, app_id, "ADMIN", "Admin")
    role_submitter = create_role(db_pg_session, app_id, "SUBMITTER", "Submitter")
    role_reviewer = create_role(db_pg_session, app_id, "REVIEWER", "Reviewer")
    # Create users with username ext_search_user[n]
    user1 = create_user(db_pg_session, "ext_search_user1", "Alice", "Smith", UserType.IDIR, "GUID1", [role_admin])
    user2 = create_user(db_pg_session, "ext_search_user2", "Bob", "Jones", UserType.BCEID, "GUID2", [role_submitter])
    user3 = create_user(db_pg_session, "ext_search_user3", "Charlie", "Brown", "CD", "GUID3", [role_reviewer]) # CD is one of BCSC type in db.
    user4 = create_user(db_pg_session, "ext_search_user4", "alice", "SMITH", UserType.IDIR, "GUID4", [role_admin, role_submitter])
    return [user1, user2, user3, user4], [role_admin, role_submitter, role_reviewer]

# ------------ Tests cases below ------------

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


def test_search_users_page_and_size_defaults(mocker, db_pg_session, allow_api_request):
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
def test_search_users_page_count_calculation(mocker, db_pg_session, allow_api_request, total, size, expected_page_count):
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

@pytest.mark.parametrize(
    "total_users,page,size,expected_user_count",
    [
        (25, 1, 10, 10),   # First page, 10 users per page
        (25, 3, 10, 5),    # Last page, 5 users left
        (25, 4, 10, 0),    # Beyond last page, no users
        (8, 1, 20, 8),     # Page size larger than total users, all users returned
        (10, 1, 10, 10),   # Page size equal to total users, all users returned
    ]
)
def test_search_users_paged_scenarios(mocker, db_pg_session, allow_api_request, total_users, page, size, expected_user_count):
    # Patch db.execute for total count
    mock_execute_total = MagicMock()
    mock_execute_total.scalar.return_value = total_users
    mock_users = [make_fam_mock_user(i) for i in range(1, total_users + 1)]

    def execute_side_effect(stmt, *args, **kwargs):
        if hasattr(stmt, "scalar"):
            return mock_execute_total
        # Simulate paged results
        offset = (page - 1) * size
        paged_users = mock_users[offset:offset + size]
        mock_paged = MagicMock()
        mock_paged.unique.return_value = mock_paged
        mock_paged.scalars.return_value = mock_paged
        mock_paged.all.return_value = paged_users
        return mock_paged
    mocker.patch.object(db_pg_session, "execute", side_effect=execute_side_effect)

    # Patch _apply_user_filters to return dummy select
    mocker.patch.object(ExtAppUserSearchService, "_apply_user_filters", side_effect=lambda stmt, params: stmt)
    # Patch joinedload (accepts any arguments, but always returns None.)
    mocker.patch("sqlalchemy.orm.joinedload", lambda *a, **kw: None)
    # _build_user_search_results will be called as normal, since input users now have correct attributes

    page_params = MagicMock()
    page_params.page = page
    page_params.size = size
    filter_params = MagicMock()

    service = ExtAppUserSearchService(db_pg_session, requester=MagicMock(), application_id=123)
    result = service.search_users(page_params, filter_params)

    assert len(result.users) == expected_user_count


@pytest.mark.parametrize(
    "idp_type,should_raise,error_code,error_msg",
    [
        (None, False, None, None),  # idp_type not set, should not raise
        ("IDIR", False, None, None),  # valid type, should not raise
        ("BCEID", False, None, None),  # valid type, should not raise
        ("BCSC", False, None, None),  # valid type, should not raise
        ("INVALID_TYPE", True, ERROR_CODE_INVALID_REQUEST_PARAMETER, "Unsupported filter idp_type"),  # invalid type, should raise
    ]
)
def test_search_users_idp_type_filter_invalid_type_exception(mocker, db_pg_session, allow_api_request,idp_type, should_raise, error_code, error_msg):
    # Patch db.execute to return mocked total count
    mock_execute = MagicMock()
    mock_execute.scalar.return_value = 0
    mocker.patch.object(db_pg_session, "execute", return_value=mock_execute)

    # Patch _build_user_search_results to return empty list
    mocker.patch.object(ExtAppUserSearchService, "_build_user_search_results", return_value=[])

    # Patch joinedload and other SQLAlchemy methods to avoid actual DB calls
    mocker.patch("sqlalchemy.orm.joinedload", lambda *a, **kw: None)

    # Prepare filter_params mock
    filter_params = MagicMock()
    filter_params.idp_type = idp_type
    filter_params.idp_username = None
    filter_params.first_name = None
    filter_params.last_name = None
    filter_params.role = None

    page_params = MagicMock()
    page_params.page = 1
    page_params.size = EXT_MIN_PAGE_SIZE

    service = ExtAppUserSearchService(db_pg_session, requester=MagicMock(), application_id=123)

    if should_raise:
        with pytest.raises(Exception) as exc_info:
            service.search_users(page_params, filter_params)
        assert error_code in str(exc_info.value)
        assert error_msg in str(exc_info.value)
    else:
        result = service.search_users(page_params, filter_params)
        assert result.meta.total == 0
        assert result.users == []

@pytest.mark.parametrize(
    "filter_kwargs, expected_count, extra_asserts",
    [
        # IDIR type
        (dict(idp_type=IDPType.IDIR, role=None, idp_username=None, first_name=None, last_name=None), 2, lambda result: all(u.idP_type == IDPType.IDIR for u in result.users)),
        # BCEID type
        (dict(idp_type=IDPType.BCEID, role=None, idp_username=None, first_name=None, last_name=None), 1, lambda result: all(u.idP_type == IDPType.BCEID for u in result.users)),
        # Username partial
        (dict(idp_type=None, role=None, idp_username="ext_search_user", first_name=None, last_name=None), 4, lambda result: all("ext_search_user" in u.idp_username for u in result.users)),
        # First name partial
        (dict(idp_type=None, role=None, idp_username=None, first_name="ali", last_name=None), 2, lambda result: all("ali" in u.first_name.lower() for u in result.users)),
        # Last name exact
        (dict(idp_type=None, role=None, idp_username=None, first_name=None, last_name="Smith"), 2, lambda result: all(u.last_name.lower() == "smith" for u in result.users)),
        # Single role
        (dict(idp_type=None, role=["ADMIN"], idp_username=None, first_name=None, last_name=None), 2, lambda result: True),
        # Multiple roles
        (dict(idp_type=None, role=["ADMIN", "SUBMITTER"], idp_username=None, first_name=None, last_name=None), 3, lambda result: True),
        # Combined fields
        (dict(idp_type=IDPType.IDIR, role=["ADMIN"], idp_username=None, first_name="alice", last_name=None), 2, lambda result: all(u.idP_type == IDPType.IDIR for u in result.users) and all("alice" in u.first_name.lower() for u in result.users) and all(any(getattr(r, "role_name", None) == "ADMIN" for r in u.roles) for u in result.users)),
        # Empty role list returns all
        (dict(idp_type=None, role=[], idp_username=None, first_name=None, last_name=None), 4, lambda result: True),
        # No filters returns all
        (dict(idp_type=None, role=None, idp_username=None, first_name=None, last_name=None), 4, lambda result: True),
    ]
)
def test_ext_app_user_search_filters(
    db_pg_session,
    allow_api_request,
    setup_users_and_roles_for_ext_user_search_tests,
    filter_kwargs, expected_count, extra_asserts
):
    def run_search(db_pg_session, requester, application_id, page, size, filter_params):
        service = ExtAppUserSearchService(db_pg_session, requester=requester, application_id=application_id)
        page_params = ExtUserSearchParamSchema(page=page, size=size)
        return service.search_users(page_params, filter_params)

    filter_params = ExtApplicationUserSearchSchema()
    for k, v in filter_kwargs.items():
        setattr(filter_params, k, v)

    result = run_search(db_pg_session, DummyRequester(), 2, 1, EXT_MIN_PAGE_SIZE, filter_params)
    assert len(result.users) == expected_count
    assert extra_asserts(result)
