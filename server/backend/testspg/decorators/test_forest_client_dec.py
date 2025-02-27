import logging
from typing import List

import pytest
from api.app.constants import AppEnv
from api.app.decorators.forest_client_dec import post_sync_forest_clients_dec
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.models.model import FamApplication
from api.app.schemas.fam_application_user_role_assignment_get import \
    FamApplicationUserRoleAssignmentGetSchema
from api.app.schemas.forest_client_integration import \
    ForestClientIntegrationFindResponseSchema
from api.app.schemas.pagination import PagedResultsSchema, PageResultMetaSchema
from mock import patch
from sqlalchemy.orm import Session
from testspg.test_data.forest_client_mock_data import (
    APP_USER_ROLE_GET_RESULTS_NO_PAGE_META, TestFcDecoratorFnResultConditions)

LOGGER = logging.getLogger(__name__)

@post_sync_forest_clients_dec
def dummy_decorated_get_app_role_assignments_fn(
    db: Session,
    some_results: List[FamApplicationUserRoleAssignmentGetSchema]
) -> PagedResultsSchema[FamApplicationUserRoleAssignmentGetSchema]:
    """ Dummy function to test decorator 'post_sync_forest_clients_dec' """
    return PagedResultsSchema(
        meta=PageResultMetaSchema(total=10,number_of_pages=1,page_number=1,page_size=10), # not test important
        results=some_results
    )

@pytest.mark.parametrize(
    "mock_fn_return, expected_results_condition",
    [
        (   # empty result.
            APP_USER_ROLE_GET_RESULTS_NO_PAGE_META[TestFcDecoratorFnResultConditions.NO_RESULT],
            TestFcDecoratorFnResultConditions.NO_RESULT
        ),
        (   # fn return with no FC in items.
            APP_USER_ROLE_GET_RESULTS_NO_PAGE_META[TestFcDecoratorFnResultConditions.NO_FC_IN_RESULTS],
            TestFcDecoratorFnResultConditions.NO_FC_IN_RESULTS
        ),
        (   # fn return with FC in items.
            APP_USER_ROLE_GET_RESULTS_NO_PAGE_META[TestFcDecoratorFnResultConditions.WITH_FC_IN_RESULTS],
            TestFcDecoratorFnResultConditions.WITH_FC_IN_RESULTS
        ),
        (   # fn return with FC in items but FC does not exist in search (legacy or not active).
            APP_USER_ROLE_GET_RESULTS_NO_PAGE_META[TestFcDecoratorFnResultConditions.WITH_FC_NOT_ACTIVE_RESULT],
            TestFcDecoratorFnResultConditions.WITH_FC_NOT_ACTIVE_RESULT
        ),
    ],
)
@patch.object(ForestClientIntegrationService, "search")
def test_should_update_client_name_for_get_app_role_assignments_fn_results(
        mock_fc_search,
        mock_fn_return: List[FamApplicationUserRoleAssignmentGetSchema],
        expected_results_condition,
        db_pg_session,
        mocker
):
    # prepare mocking
    fcapi_search_return_dict = [
        ForestClientIntegrationFindResponseSchema(
            clientName=f"client_{fc.forest_client_number}", clientNumber=fc.forest_client_number, clientStatusCode="ACT", clientTypeCode="C"
        ).model_dump()
        for fc in [item.role.forest_client for item in mock_fn_return] if fc is not None
    ]
    if any(fcapi_search_return_dict):
        mock_fc_search.return_value = fcapi_search_return_dict

    mocker.patch("api.app.decorators.forest_client_dec.crud_application.get_application",
                 return_value=FamApplication(app_environment=AppEnv.APP_ENV_TYPE_DEV))

    # call decorated function
    fn_dec_return = dummy_decorated_get_app_role_assignments_fn(db=db_pg_session, some_results=mock_fn_return)

    if expected_results_condition is not TestFcDecoratorFnResultConditions.WITH_FC_IN_RESULTS:
        # expect decorated results is the same and no forest client name update.
        assert fn_dec_return.results == APP_USER_ROLE_GET_RESULTS_NO_PAGE_META[expected_results_condition]
        if (expected_results_condition is TestFcDecoratorFnResultConditions.WITH_FC_NOT_ACTIVE_RESULT):
            assert mock_fc_search.call_count == 1
        else:
            assert mock_fc_search.call_count == 0

    else:
        # expect decorated results contains client name update.
        results_client_name_set =  {fc.client_name for fc in [item.role.forest_client for item in fn_dec_return.results] if fc is not None}
        expeced_client_name_set = {item["clientName"] for item in fcapi_search_return_dict}
        results_client_name_set == expeced_client_name_set
        assert mock_fc_search.call_count == 1