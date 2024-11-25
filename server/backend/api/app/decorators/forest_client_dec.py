import logging
from typing import List

from api.app.crud import crud_utils
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.schemas.fam_application_user_role_assignment_get import \
    FamApplicationUserRoleAssignmentGetSchema
from api.app.schemas.forest_client_integration import (
    ForestClientIntegrationFindResponseSchema,
    ForestClientIntegrationSearchParmsSchema)
from api.app.schemas.pagination import PagedResultsSchema

LOGGER = logging.getLogger(__name__)

def post_sync_forest_clients_dec(func):
    """
    A decorator to perform post action on syncing forest client details from external Forest Client API search.
    Only intended for use at functions with return type of 'PagedResultsSchema[FamApplicationUserRoleAssignmentGetSchema]'
    """
    def wrapper(*args, **kwargs):
        func_return: PagedResultsSchema[FamApplicationUserRoleAssignmentGetSchema] = func(*args, **kwargs)
        func_return.results = __post_sync_forest_clients(func_return.results)
        return func_return
    return wrapper

def __post_sync_forest_clients(result_list: List[FamApplicationUserRoleAssignmentGetSchema]):
    if not result_list:
        return result_list

    LOGGER.debug("Start post syncing with Forest Client API...")

    # Collecting possible forest client numbers.
    # Each role in function's result list (of type: FamApplicationUserRoleAssignmentGetSchema) could be scoped
    # to forest client number or could have no scope. The collected number could be duplicated but here we don't
    # need to care. The FC API will not return duplicated search items.
    # Below is a mapping function: collect each forest client number from each item or None.
    map_to_fc = lambda item: item.role.forest_client.forest_client_number if item.role.forest_client else None
    search_forest_client_numbers = [
        fcn for fcn in [map_to_fc(item) for item in result_list] if fcn
    ]  # loop to collect and filter out 'None'

    # Do FC API search
    application = result_list[0].role.application
    api_instance_env = crud_utils.use_api_instance_by_app(application)
    forest_client_integration_service = ForestClientIntegrationService(api_instance_env)
    fc_search_params = ForestClientIntegrationSearchParmsSchema(
        forest_client_numbers=search_forest_client_numbers,
        size=len(search_forest_client_numbers)
    )

    # Note, FC API result items are not 1 to 1 (duplicates and non-exist will be filtered out from external
    #  FC API search). Example return:
    # [{'clientNumber': '00001011', 'clientName': 'AKIECA EXPLORERS LTD.', 'clientStatusCode': 'ACT', 'clientTypeCode': 'C'}]
    fc_search_results: List[ForestClientIntegrationFindResponseSchema] = forest_client_integration_service.search(fc_search_params)

    # Only sync client_name when there is a FC search result
    if fc_search_results:
        # Transform FC search result (won't have duplicates) into a dict for easy indexing e.g.,: {00001011: 'AKIECA EXPLORERS LTD.'}
        fc_search_client_name_dict = {fc["clientNumber"]: fc["clientName"] for fc in fc_search_results}

        # Update client_name on each using 'fc_search_client_name_dict'
        for item in result_list:
            if item.role.forest_client:
                fcn = item.role.forest_client.forest_client_number
                item.role.forest_client.client_name = fc_search_client_name_dict[fcn]

    return result_list
