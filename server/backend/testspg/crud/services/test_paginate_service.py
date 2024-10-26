import logging
from enum import Enum

import pytest
from api.app.constants import DEFAULT_PAGE_SIZE, MIN_PAGE
from api.app.crud.services.paginate_service import PaginateService
from api.app.models.model import FamUser
from api.app.schemas.fam_user_info import FamUserInfoSchema
from api.app.schemas.pagination import PageParamsSchema
from sqlalchemy import Select, not_, select
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)

"""
These suites of tests use FamUser (fam_user table) for easy testing on the 'PaginateService'
to avoid complicated test data setup.
Note:
For testing on pagination some mock data are added to the session (no committed). However, due to
existing testcontainer database already has some seeding from local test flyway, it has to be
taken into consideration for tests cases to verify the correct results.
"""
# enum and schema needed only within this suites of tests.
class TestUserSortByEnum(str, Enum):
    USER_NAME = "user_name"
    DOMAIN = "user_type_code"
    EMAIL = "email"

class TestUserPageParamsSchema(PageParamsSchema):
    sort_by: TestUserSortByEnum | None

# base_query to be used only within this suites of tests.
test_base_query = Select(FamUser)
TEST_USER_NAME_PREFIX = "TEST_USER_"

def __get_number_of_pages(count: int, page_size) -> int:
    rest = count % page_size
    quotient = count // page_size
    return quotient if not rest else quotient + 1

def __get_existing_testdb_seeded_users(db_pg_session: Session):
    return db_pg_session.scalars(select(FamUser).filter(not_(FamUser.user_name.ilike(f"%{TEST_USER_NAME_PREFIX}%")))).all()

# -------------------------------------------------------------------------------------------------------------------------

def test_get_paginated_results__users_paged_with_default_pagination(db_pg_session: Session, load_test_users):
    """
    This case tests on 'PaginateService.get_paginated_results' for default page_params.

    """
    # this 'load_test_users' fixture loads bunch of users into db session for testing.
    mock_user_data_load = load_test_users
    existing_testdb_seeded_users = __get_existing_testdb_seeded_users(db_pg_session)
    default_page_params = TestUserPageParamsSchema(
        page=MIN_PAGE, size=DEFAULT_PAGE_SIZE, search=None, sort_by=None, sort_order=None
    )

    paginated_service = PaginateService(db_pg_session, test_base_query, None, None, default_page_params)
    paged_result = paginated_service.get_paginated_results(FamUserInfoSchema)

    assert paged_result is not None
    result_data = paged_result.results
    meta = paged_result.meta
    assert result_data is not None
    total_db_user_rows = len(mock_user_data_load) + len(existing_testdb_seeded_users)
    assert meta.total == total_db_user_rows
    assert meta.page_number == MIN_PAGE
    assert meta.page_size == DEFAULT_PAGE_SIZE
    assert len(result_data) == DEFAULT_PAGE_SIZE
    expected_num_of_pages = __get_number_of_pages(total_db_user_rows, DEFAULT_PAGE_SIZE)
    assert meta.number_of_pages == expected_num_of_pages


@pytest.mark.parametrize(
    "test_page_params, expected_results_size",
    [
        (TestUserPageParamsSchema(
            page=2, size=5, search=None, sort_by=None, sort_order=None
        ), 5),
        (TestUserPageParamsSchema(
            page=3, size=25, search=None, sort_by=None, sort_order=None
        ), 25),
        (TestUserPageParamsSchema(  # asuume page is out of range from total rows from the test setup
            page=50, size=100, search=None, sort_by=None, sort_order=None
        ), 0),
    ],
)
def test_get_paginated_results__users_paged_with_non_default_pagination(
    test_page_params: TestUserPageParamsSchema, expected_results_size: int,
    db_pg_session: Session, load_test_users
):
    """
    This case tests on 'PaginateService.get_paginated_results' for non-default page_params.
    """
    mock_user_data_load = load_test_users
    existing_testdb_seeded_users = __get_existing_testdb_seeded_users(db_pg_session)

    paginated_service = PaginateService(db_pg_session, test_base_query, None, None, test_page_params)
    paged_result = paginated_service.get_paginated_results(FamUserInfoSchema)

    assert paged_result is not None
    result_data = paged_result.results
    meta = paged_result.meta
    assert result_data is not None
    total_db_user_rows = len(mock_user_data_load) + len(existing_testdb_seeded_users)
    assert meta.total == total_db_user_rows
    assert meta.page_number == test_page_params.page
    assert meta.page_size == test_page_params.size
    assert len(result_data) == expected_results_size
    expected_num_of_pages = __get_number_of_pages(total_db_user_rows, test_page_params.size)
    assert meta.number_of_pages == expected_num_of_pages
