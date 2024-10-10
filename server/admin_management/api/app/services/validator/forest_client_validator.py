import logging
from typing import List, Union

from api.app.constants import FOREST_CLIENT_STATUS
from api.app.schemas.schemas import ForestClientIntegrationFindResponse

LOGGER = logging.getLogger(__name__)


def forest_client_number_exists(
    forest_client_find_result: List[ForestClientIntegrationFindResponse],
) -> bool:
    # Exact client number search - should only contain 1 result.
    return len(forest_client_find_result) == 1


def forest_client_active(
    forest_client_find_result: List[ForestClientIntegrationFindResponse],
) -> bool:
    return (
        (
            forest_client_find_result[0][FOREST_CLIENT_STATUS["KEY"]]
            == FOREST_CLIENT_STATUS["CODE_ACTIVE"]
        )
        if forest_client_number_exists(forest_client_find_result)
        else False
    )


def get_forest_client_status(
    forest_client_find_result: List[ForestClientIntegrationFindResponse],
) -> Union[str, None]:
    return (
        forest_client_find_result[0][FOREST_CLIENT_STATUS["KEY"]]
        if forest_client_number_exists(forest_client_find_result)
        else None
    )
