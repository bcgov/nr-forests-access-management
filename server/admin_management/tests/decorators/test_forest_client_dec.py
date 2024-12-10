import logging
from typing import List

import pytest
from api.app.decorators.forest_client_dec import post_sync_forest_clients_dec
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.schemas.pagination import PagedResultsSchema, PageResultMetaSchema
from api.app.schemas.schemas import FamAccessControlPrivilegeGetResponse
from mock import patch
from tests.test_data.forest_client_mock_data import (
    APP_DELEGATED_ADMIN_ROLE_GET_RESULTS_NO_PAGE_META,
    TestAccessControlResultDictKeys)

LOGGER = logging.getLogger(__name__)

@post_sync_forest_clients_dec
def dummy_delegated_admin_assignment_fn_to_be_decorated(
    some_results: List[FamAccessControlPrivilegeGetResponse]
) -> PagedResultsSchema[FamAccessControlPrivilegeGetResponse]:
    """ Dummy function to test decorator 'post_sync_forest_clients_dec' can handle
        'AccessControlPrivilegeService.get_paged_delegated_admin_assignment_by_application_id()'
    """
    return PagedResultsSchema[FamAccessControlPrivilegeGetResponse](
        meta=PageResultMetaSchema(total=10,number_of_pages=1,page_number=1,page_size=10), # not test important
        results=some_results
    )

@pytest.mark.parametrize(
    "mock_fn_return, expected_results_condition",
    [
        (   # empty result.
            APP_DELEGATED_ADMIN_ROLE_GET_RESULTS_NO_PAGE_META[TestAccessControlResultDictKeys.NO_RESULT],
            TestAccessControlResultDictKeys.NO_RESULT
        ),
        (   # fn return with no FC in items.
            APP_DELEGATED_ADMIN_ROLE_GET_RESULTS_NO_PAGE_META[TestAccessControlResultDictKeys.NO_FC_IN_RESULTS],
            TestAccessControlResultDictKeys.NO_FC_IN_RESULTS
        ),
        (   # fn return with FC in items.
            APP_DELEGATED_ADMIN_ROLE_GET_RESULTS_NO_PAGE_META[TestAccessControlResultDictKeys.WITH_FC_IN_RESULTS],
            TestAccessControlResultDictKeys.WITH_FC_IN_RESULTS
        ),
        (   # fn return with FC in items but FC does not exist in search (legacy or not active).
            APP_DELEGATED_ADMIN_ROLE_GET_RESULTS_NO_PAGE_META[TestAccessControlResultDictKeys.WITH_FC_NOT_ACTIVE_RESULT],
            TestAccessControlResultDictKeys.WITH_FC_NOT_ACTIVE_RESULT
        ),
    ],
)
@patch.object(ForestClientIntegrationService, "search")
def test_should_update_client_name_for_forest_client_fn_results(
        mock_fc_search,
        mock_fn_return: List[FamAccessControlPrivilegeGetResponse],
        expected_results_condition,
):
    # prepare mocking
    fcapi_search_return_dict = [
        {
            "clientName": f"client_{fc.forest_client_number}",
            "clientNumber": fc.forest_client_number,
            "clientStatusCode": "ACT",
            "clientTypeCode": "C"
        }
        for fc in [item.role.forest_client for item in mock_fn_return] if fc is not None
    ]
    if any(fcapi_search_return_dict):
        mock_fc_search.return_value = fcapi_search_return_dict

    # call decorated function
    fn_dec_return = dummy_delegated_admin_assignment_fn_to_be_decorated(some_results=mock_fn_return)

    if expected_results_condition is not TestAccessControlResultDictKeys.WITH_FC_IN_RESULTS:
        # expect decorated results is the same and no forest client name update.
        assert fn_dec_return.results == APP_DELEGATED_ADMIN_ROLE_GET_RESULTS_NO_PAGE_META[expected_results_condition]
        if (expected_results_condition is TestAccessControlResultDictKeys.WITH_FC_NOT_ACTIVE_RESULT):
            assert mock_fc_search.call_count == 1
        else:
            assert mock_fc_search.call_count == 0

    else:
        # expect decorated results contains client name update.
        results_client_name_set =  {fc.client_name for fc in [item.role.forest_client for item in fn_dec_return.results] if fc is not None}
        expeced_client_name_set = {item["clientName"] for item in fcapi_search_return_dict}
        results_client_name_set == expeced_client_name_set
        assert mock_fc_search.call_count == 1