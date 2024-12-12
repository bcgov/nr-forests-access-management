import json
import logging
from typing import List

from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.routers.router_utils import get_api_instance_env
from api.app.schemas import FamForestClientSchema
from api.app.schemas.forest_client_integration import \
    ForestClientIntegrationSearchParmsSchema
from fastapi import APIRouter, Depends, Query

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search", response_model=List[FamForestClientSchema])
def search(
    client_number: str = Query(min_length=3, max_length=8),
    api_instance_env=Depends(get_api_instance_env),
):
    """
    Forest Client(s) search (by defined query parameter(s)).
    param: 'client_number=[query_value]'
           Note! Current Forest Client API limits it to exact search for a whole 8-digits number.
    return: List of found FamForestClient. However, currently only 1 exact match returns.
    """
    LOGGER.debug(
        f"Searching Forest Clients with parameter client_number: {client_number}"
    )
    fc_api = ForestClientIntegrationService(api_instance_env)
    fc_search_params = ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[client_number])
    fc_json_list = fc_api.search(fc_search_params)  # json object List
    forest_clients = list(map(__map_api_results, fc_json_list))
    LOGGER.debug(f"Returning {len(forest_clients)} result.")
    return forest_clients


def __map_api_results(item) -> FamForestClientSchema:
    """
    Private method to map api result to FamForestClientSchema
    """
    parsed = json.loads(
        json.dumps(item),  # need json string format, so dumps from 'dic' type 'item'.
        object_hook=FamForestClientSchema.from_api_json,
    )
    return parsed
