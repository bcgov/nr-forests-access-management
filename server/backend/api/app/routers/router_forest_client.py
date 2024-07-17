import json
import logging
from typing import List

from api.app.constants import AppEnv
from api.app.integration.forest_client.forest_client import ForestClientService
from fastapi import APIRouter, Query

from .. import schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search", response_model=List[schemas.FamForestClient])
def search(
    client_number: str = Query(min_length=3, max_length=8),
    app_env: AppEnv = AppEnv.APP_ENV_TYPE_TEST
):
    """
    Forest Client(s) search (by defined query parameter(s)).

    param: 'client_number=[query_value]'
           Note! Current Forest Client API limits it to exact search for a whole 8-digits number.

    return: List of found FamForestClient. However, currently only 1 exact match returns.
    """
    LOGGER.debug(f"Searching Forest Clients with parameter client_number: {client_number}")
    fc_api = ForestClientService(app_env)
    fc_json_list = fc_api.find_by_client_number(client_number)  # json object List
    forest_clients = list(map(__map_api_results, fc_json_list))
    LOGGER.debug(f"Returning {len(forest_clients)} result.")
    return forest_clients


def __map_api_results(item) -> schemas.FamForestClient:
    """
    Private method to map api result to schemas.FamForestClient
    """
    parsed = json.loads(
        json.dumps(item),  # need json string format, so dumps from 'dic' type 'item'.
        object_hook=schemas.FamForestClient.from_api_json
    )
    return parsed

