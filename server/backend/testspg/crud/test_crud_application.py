import logging

import pytest
from api.app.constants import (DEFAULT_PAGE_SIZE, MIN_PAGE, SortOrderEnum,
                               UserRoleSortByEnum, UserType)
from api.app.crud import crud_application
from api.app.crud.services.paginate_service import PaginateService
from api.app.schemas.pagination import UserRolePageParamsSchema
from api.app.schemas.requester import RequesterSchema
from sqlalchemy.orm import Session
from testspg.constants import (FOM_DEV_APPLICATION_ID,
                               NOT_EXIST_APPLICATION_ID, TEST_REQUESTER)
from testspg.utils import contains_any_insensitive, is_sorted_with

LOGGER = logging.getLogger(__name__)

TEST_APPLICATION_NAME_NOT_FOUND = "NOT_FOUND"
TEST_APPLICATION_NAME_FAM = "FAM"
TEST_APPLICATION_ID_FAM = 1


def test_get_application(db_pg_session: Session):
    app_by_id = crud_application.get_application(
        db=db_pg_session, application_id=TEST_APPLICATION_ID_FAM
    )
    assert app_by_id.application_id == TEST_APPLICATION_ID_FAM
    assert app_by_id.application_name == TEST_APPLICATION_NAME_FAM

    app_by_id = crud_application.get_application(
        db=db_pg_session, application_id=NOT_EXIST_APPLICATION_ID
    )
    assert app_by_id is None


@pytest.mark.parametrize(
    "test_page_params, expected_condition",
    [
        (UserRolePageParamsSchema(page=MIN_PAGE, size=DEFAULT_PAGE_SIZE, search=None, sort_by=None, sort_order=None), # default
        {"found": True, "within_range": True}),
        (UserRolePageParamsSchema(page=MIN_PAGE, size=DEFAULT_PAGE_SIZE, search="NOT_EXISTS", sort_by=None, sort_order=None), # no result found
        {"found": False, "within_range": True}),
        (UserRolePageParamsSchema(page=1000000, size=100, search=None, sort_by=None, sort_order=None), # page out of range
        {"found": True, "within_range": False}),
        (UserRolePageParamsSchema(page=3, size=10, search=None, sort_by=None, sort_order=None),
        {"found": True, "within_range": True}),
        (UserRolePageParamsSchema(page=MIN_PAGE, size=10, search=None, sort_by=UserRoleSortByEnum.USER_NAME, sort_order=SortOrderEnum.ASC),
        {"found": True, "within_range": True, "sort_by_result_schema_attr": "user.user_name"}),
        (UserRolePageParamsSchema(page=MIN_PAGE, size=10, search=None, sort_by=UserRoleSortByEnum.ROLE_DISPLAY_NAME, sort_order=SortOrderEnum.DESC),
        {"found": True, "within_range": True, "sort_by_result_schema_attr": "role.display_name"}),
        (UserRolePageParamsSchema(page=MIN_PAGE, size=10, search="IDIR", sort_by=UserRoleSortByEnum.USER_NAME, sort_order=SortOrderEnum.DESC),
        {"found": True, "within_range": True, "sort_by_result_schema_attr": "user.user_name"}),
        (UserRolePageParamsSchema(page=MIN_PAGE, size=100, search="submitter", sort_by=UserRoleSortByEnum.FOREST_CLIENT_NUMBER, sort_order=SortOrderEnum.DESC),
        {"found": True, "within_range": True, "sort_by_result_schema_attr": "role.forest_client.forest_client_number"}),
        (UserRolePageParamsSchema(page=MIN_PAGE, size=10, search="not_fund", sort_by=UserRoleSortByEnum.EMAIL, sort_order=SortOrderEnum.ASC),
        {"found": False, "within_range": True, "sort_by_result_schema_attr": "user.email"}),
    ],
)
def test_get_application_role_assignments_on_pagination(
    mocker, db_pg_session: Session, load_fom_dev_user_role_test_data, test_page_params: UserRolePageParamsSchema, expected_condition
):
    session = db_pg_session
    dummy_test_requester = RequesterSchema(**TEST_REQUESTER, user_type_code=UserType.IDIR)

    mocker.patch("api.app.crud.crud_utils.is_app_admin", return_value=True)
    paginate_service_get_paginated_results_fn_spy = mocker.spy(PaginateService, 'get_paginated_results')

    # Important! the `.__wrapped__` contains the original function (without decorated) so tests can use it.
    # See note at 'forest_client_dec.py'
    original_get_application_role_assignments_fn = crud_application.get_application_role_assignments.__wrapped__
    paged_results = original_get_application_role_assignments_fn(
        db=session, application_id=FOM_DEV_APPLICATION_ID, requester=dummy_test_requester, page_params=test_page_params
    )

    assert paginate_service_get_paginated_results_fn_spy.call_count == 1
    assert paged_results is not None
    assert paged_results == paginate_service_get_paginated_results_fn_spy.spy_return
    result_data = paged_results.results
    meta = paged_results.meta
    assert result_data is not None
    assert meta.page_number == test_page_params.page
    assert meta.page_size == test_page_params.size
    if not expected_condition["within_range"]:
        assert result_data == []

    if not expected_condition["found"]:
        assert meta.total == 0
        assert result_data == []
    else:
        assert meta.total > 0

    # verify sorting
    if test_page_params.sort_by:
        sort_order = test_page_params.sort_order
        sort_by_result_schema_attr = expected_condition["sort_by_result_schema_attr"]
        assert all(
            is_sorted_with(result_data[i], result_data[i+1], sort_by_result_schema_attr, sort_order)
            for i in range(len(result_data) - 1)
        )

    # verify filtering
    if test_page_params.search:
        # verify filtering: checks all of 'result_data' item has at least one attribute value
        # (within type FamApplicationUserRoleAssignmentGetSchema) contains filtering keyword.
        search_attributes = [
            "create_date",
            "user.user_name",
            "user.user_type_relation.user_type_code",
            "user.email",
            "user.first_name",
            "user.last_name",
            "role.display_name",
            "role.forest_client.forest_client_number"
        ]
        assert all(
            contains_any_insensitive(result_data[i], search_attributes, test_page_params.search)
            for i in range(len(result_data) - 1)
        )
