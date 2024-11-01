import logging
from enum import Enum
from typing import List, Optional

import pytest
from api.app.constants import (DEFAULT_PAGE_SIZE, MIN_PAGE, SortOrderEnum,
                               UserType)
from api.app.crud.services.paginate_service import PaginateService
from api.app.models.model import FamUser
from api.app.schemas.pagination import PageParamsSchema
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Select, not_, or_, select
from sqlalchemy.orm import Session
from testspg.constants import (TEST_USER_EMAIL_SUFFIX,
                               TEST_USER_NAME_BCEID_PREFIX,
                               TEST_USER_NAME_IDIR_PREFIX,
                               TEST_USER_NAME_PREFIX)
from testspg.utils import (contains_any_insensitive,
                           get_existing_testdb_seeded_users, is_sorted_with)

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

# test schema type used only in this test file.
class TestFamUserInfoSchema(BaseModel):
    user_id: int
    user_name: str
    user_type_code: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )

USER_SORT_BY_MAPPED_COLUMN = {
    TestUserSortByEnum.USER_NAME: FamUser.user_name,  # default
    TestUserSortByEnum.DOMAIN: FamUser.user_type_code,
    TestUserSortByEnum.EMAIL: FamUser.email
}

# base_query to be used only within this suites of tests.
test_base_query = Select(FamUser)

def __get_number_of_pages(count: int, page_size) -> int:
    rest = count % page_size
    quotient = count // page_size
    return quotient if not rest else quotient + 1

def __build_test_filter_criteria(page_params: TestUserPageParamsSchema):
    search_keyword = page_params.search
    filter_on_columns = USER_SORT_BY_MAPPED_COLUMN.values()
    return (
        or_(
            *list(map(lambda column: column.ilike(f"%{search_keyword}%"), filter_on_columns))
        )
        if search_keyword is not None
        else None
    )

def __get_number_of_pages(count: int, page_size: int) -> int:
    rest = count % page_size
    quotient = count // page_size
    return quotient if not rest else quotient + 1

def sort_list(list: List[FamUser], sort_by, sort_order):
    def by_key(e):
        return getattr(e, sort_by)

    list.sort(reverse=(sort_order == SortOrderEnum.DESC), key=by_key)
    return list

# -------------------------------------------------------------------------------------------------------------------------

def test_get_paginated_results__users_paged_with_default_pagination(db_pg_session: Session, load_test_users):
    """
    This case tests on 'PaginateService.get_paginated_results' for default page_params.

    """
    # this 'load_test_users' fixture loads bunch of users into db session for testing.
    mock_user_data_load = load_test_users["idir_users"] + load_test_users["bceid_users"]
    existing_testdb_seeded_users = get_existing_testdb_seeded_users(db_pg_session, TEST_USER_NAME_PREFIX)
    default_page_params = TestUserPageParamsSchema(
        page=MIN_PAGE, size=DEFAULT_PAGE_SIZE, search=None, sort_by=None, sort_order=None
    )

    paginated_service = PaginateService(db_pg_session, test_base_query, None, USER_SORT_BY_MAPPED_COLUMN, default_page_params)
    paged_result = paginated_service.get_paginated_results(TestFamUserInfoSchema)

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
        (TestUserPageParamsSchema(  # assume page is out of range from total rows from the test setup
            page=100000, size=100, search=None, sort_by=None, sort_order=None
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
    mock_user_data_load = load_test_users["idir_users"] + load_test_users["bceid_users"]
    existing_testdb_seeded_users = get_existing_testdb_seeded_users(db_pg_session, TEST_USER_NAME_PREFIX)

    paginated_service = PaginateService(db_pg_session, test_base_query, None, USER_SORT_BY_MAPPED_COLUMN, test_page_params)
    paged_result = paginated_service.get_paginated_results(TestFamUserInfoSchema)

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


@pytest.mark.parametrize(
    "test_page_params, sort_by_attribute",
    [
        (TestUserPageParamsSchema(
            page=1, size=10, search=None, sort_by=TestUserSortByEnum.USER_NAME, sort_order=SortOrderEnum.ASC
        ), "user_name"),
        (TestUserPageParamsSchema(
            page=1, size=10, search=None, sort_by=TestUserSortByEnum.USER_NAME, sort_order=SortOrderEnum.DESC
        ), "user_name"),
        (TestUserPageParamsSchema(
            page=1, size=10, search=None, sort_by=TestUserSortByEnum.DOMAIN, sort_order=SortOrderEnum.ASC
        ), "user_type_code"),
        (TestUserPageParamsSchema(
            page=1, size=10, search=None, sort_by=TestUserSortByEnum.DOMAIN, sort_order=SortOrderEnum.DESC
        ), "user_type_code"),
        (TestUserPageParamsSchema(
            page=1, size=10, search=None, sort_by=TestUserSortByEnum.EMAIL, sort_order=SortOrderEnum.ASC
        ), "email"),
        (TestUserPageParamsSchema(
            page=1, size=10, search=None, sort_by=TestUserSortByEnum.EMAIL, sort_order=SortOrderEnum.DESC
        ), "email")
    ],
)
def test_get_paginated_results__users_paged_with_sorting(
    test_page_params: TestUserPageParamsSchema, sort_by_attribute: str, db_pg_session: Session, load_test_users
):
    """
    This case tests on 'PaginateService.get_paginated_results' for sorting.
    """
    mock_user_data_load = load_test_users["idir_users"] + load_test_users["bceid_users"]
    existing_testdb_seeded_users = get_existing_testdb_seeded_users(db_pg_session, TEST_USER_NAME_PREFIX)

    paginated_service = PaginateService(db_pg_session, test_base_query, None, USER_SORT_BY_MAPPED_COLUMN, test_page_params)
    paged_result = paginated_service.get_paginated_results(TestFamUserInfoSchema)

    assert paged_result is not None
    result_data = paged_result.results
    meta = paged_result.meta
    assert result_data is not None
    total_db_user_rows = len(mock_user_data_load) + len(existing_testdb_seeded_users)
    assert meta.total == total_db_user_rows
    assert meta.page_number == test_page_params.page
    assert meta.page_size == test_page_params.size
    # verify sorting
    sort_order = test_page_params.sort_order
    assert all(
        is_sorted_with(result_data[i], result_data[i+1], sort_by_attribute, sort_order)
        for i in range(len(result_data) - 1)
    )


@pytest.mark.parametrize(
    "test_page_params",
    [
        TestUserPageParamsSchema(
            page=MIN_PAGE, size=DEFAULT_PAGE_SIZE, search="NOT_EXISTS", sort_by=None, sort_order=None
        ),
        TestUserPageParamsSchema(
            page=MIN_PAGE, size=5, search=TEST_USER_NAME_PREFIX, sort_by=TestUserSortByEnum.USER_NAME, sort_order=SortOrderEnum.ASC
        ),
        TestUserPageParamsSchema(
            page=MIN_PAGE, size=5, search=UserType.BCEID.lower(), sort_by=TestUserSortByEnum.USER_NAME, sort_order=SortOrderEnum.ASC
        ),
        TestUserPageParamsSchema(
            page=MIN_PAGE, size=5, search=TEST_USER_EMAIL_SUFFIX.upper(), sort_by=TestUserSortByEnum.USER_NAME, sort_order=SortOrderEnum.ASC
        ),
        TestUserPageParamsSchema(
            page=3, size=5, search=TEST_USER_NAME_IDIR_PREFIX, sort_by=TestUserSortByEnum.EMAIL, sort_order=SortOrderEnum.ASC
        ),
        TestUserPageParamsSchema(
            page=3, size=5, search=TEST_USER_NAME_BCEID_PREFIX, sort_by=TestUserSortByEnum.EMAIL, sort_order=SortOrderEnum.DESC
        ),
    ],
)
def test_get_paginated_results__users_paged_with_filtering(
    test_page_params: TestUserPageParamsSchema, db_pg_session: Session, load_test_users, mocker
):
    """
    This case tests on 'PaginateService.get_paginated_results' for filtering.
    Filtering is based on provided 'filter_by_criteria' for the service which search with keyword
    contained in "user_name", "user_type" or "email"
    """
    mock_user_data_load = load_test_users["idir_users"] + load_test_users["bceid_users"]
    existing_testdb_seeded_users = get_existing_testdb_seeded_users(db_pg_session, TEST_USER_NAME_PREFIX)
    search_keyword = test_page_params.search

    paginated_service = PaginateService(
        db_pg_session, test_base_query,
        __build_test_filter_criteria(test_page_params), USER_SORT_BY_MAPPED_COLUMN, test_page_params
    )
    paged_result = paginated_service.get_paginated_results(TestFamUserInfoSchema)

    assert paged_result is not None
    result_data = paged_result.results
    meta = paged_result.meta
    assert result_data is not None

    search_attributes = list(map(lambda item: item.value, TestUserSortByEnum))
    db_filtered_users = list(filter(
        lambda user: user if contains_any_insensitive(user, search_attributes, search_keyword) else None,
        mock_user_data_load + existing_testdb_seeded_users
    ))
    assert meta.total == len(db_filtered_users)
    assert meta.page_number == test_page_params.page
    assert meta.page_size == test_page_params.size

    if meta.total > 0:
        # verify filtering: checks all of 'result_data' item has at least one attribute value
        # contains filtering keyword.
        assert all(
            contains_any_insensitive(result_data[i], search_attributes, search_keyword)
            for i in range(len(result_data) - 1)
        )

        assert meta.number_of_pages == __get_number_of_pages(meta.total, meta.page_size)

        if test_page_params.sort_by:
            db_filtered_users = sort_list(
                db_filtered_users, sort_by=test_page_params.sort_by, sort_order=test_page_params.sort_order
            )
        offset = (meta.page_number - 1) * meta.page_size
        db_paged_users = []
        if meta.total > offset:
            max_range = offset + meta.page_size
            max_range = meta.total if max_range >= meta.total else max_range
            db_paged_users = [db_filtered_users[i] for i in range(offset, max_range)]
        db_paged_users_id_set = { du.user_id for du in db_paged_users}
        result_users_id_set = { rd.user_id for rd in result_data}
        assert len(result_users_id_set.difference(db_paged_users_id_set)) == 0
