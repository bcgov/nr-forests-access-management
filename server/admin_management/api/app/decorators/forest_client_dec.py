import functools
import logging

from api.app.constants import AdminRoleAuthGroup
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.schemas.forest_client_integration import \
    ForestClientIntegrationSearchParmsSchema
from api.app.schemas.schemas import AdminUserAccessResponse
from api.app.services import utils_service

LOGGER = logging.getLogger(__name__)

def post_sync_forest_clients_dec(original_func):
    """
    A decorator to perform post action on syncing forest client details from external Forest Client API search.

    Important! using the Python `@functools.wraps(original_func)` feature. This makes decorated_func get almost all the
          original function's metadata and makes it possible and easier for testing original function in isolation.
          Ref: https://docs.python.org/3/library/functools.html#functools.wraps
    """
    @functools.wraps(original_func)
    def decorated_func(*args, **kwargs):
        func_return: AdminUserAccessResponse = original_func(*args, **kwargs)
        func_return = __post_sync_forest_clients(func_return)
        return func_return
    return decorated_func

def __post_sync_forest_clients(func_return: AdminUserAccessResponse):
    if not func_return:
        return func_return

    LOGGER.debug("Start post syncing with Forest Client API...")

    # Collecting possible forest client numbers.
    # Each role in function's return could be scoped to forest client number or could have no scope.
    # The collected forest client number could be duplicated, the FC API will not return duplicated search items.

    # Only application roles in auth_key=AdminRoleAuthGroup.DELEGATED_ADMIN could exist forest client number.
    delegatged_admin_grants = next(
        filter(lambda access_grant: access_grant.auth_key == AdminRoleAuthGroup.DELEGATED_ADMIN , func_return.access),
        None
    )

    if delegatged_admin_grants:
        for app_grants in delegatged_admin_grants.grants:
            # find out forest_client_numbers within each privilege given to an application.
            search_forest_client_numbers = [
               forest_client.forest_client_number for role in app_grants.roles if role.forest_clients
               for forest_client in role.forest_clients
            ]

            # Do FC API search
            api_instance_env = utils_service.use_api_instance_by_app_env(app_grants.application.env)
            forest_client_integration_service = ForestClientIntegrationService(api_instance_env)
            fc_search_params = ForestClientIntegrationSearchParmsSchema(
                forest_client_numbers=search_forest_client_numbers,
                size=len(search_forest_client_numbers)
                # currently no need to specify FC API 'page'. it can search more than 50 and return in the first page.
            )

            # Note, FC API result items are not 1 to 1 (duplicates and non-exist will be filtered out from external
            #  FC API search). Example return:
            # [{'clientNumber': '00001011', 'clientName': 'AKIECA EXPLORERS LTD.', 'clientStatusCode': 'ACT', 'clientTypeCode': 'C'}]
            fc_search_results = forest_client_integration_service.search(fc_search_params)

            # Only update client_name when there is a FC search result
            if fc_search_results:
                # Transform FC search result (won't have duplicates) into a dict for easy indexing e.g.,: {00001011: 'AKIECA EXPLORERS LTD.'}
                fc_search_client_name_dict = {fc["clientNumber"]: fc["clientName"] for fc in fc_search_results}

                # Update client_name on each using 'fc_search_client_name_dict'
                for role in app_grants.roles:
                    if role.forest_clients:
                        for forest_client in role.forest_clients:
                            fcn = forest_client.forest_client_number
                            forest_client.client_name = fc_search_client_name_dict.get(fcn)

    return func_return
