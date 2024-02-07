import logging
from typing import List, Union

from api.app.integration.forest_client_integration import ForestClientService
from api.app.constants import FOREST_CLIENT_STATUS
from api.app.schemas import ForestClientValidatorResponse


LOGGER = logging.getLogger(__name__)


class ForestClientValidator:
    """
    Purpose: Validate if the forest client number is active.
    Cautious: Do not instantiate the class for more than one time per request.
              It calls Forest Client API remotely if needs to.
    """

    LOGGER = logging.getLogger(__name__)

    def __init__(self):
        self.fc_api = ForestClientService()

    def find_forest_client_number(
        self, forest_client_number: str
    ) -> List[ForestClientValidatorResponse]:
        # Note - this value should already be validated from schema input validation.
        return self.fc_api.find_by_client_number(forest_client_number)

    def forest_client_number_exists(
        self, forest_client_find_result: List[ForestClientValidatorResponse]
    ) -> bool:
        # Exact client number search - should only contain 1 result.
        return len(forest_client_find_result) == 1

    def forest_client_active(
        self, forest_client_find_result: List[ForestClientValidatorResponse]
    ) -> bool:
        return (
            (
                forest_client_find_result[0][FOREST_CLIENT_STATUS["KEY"]]
                == FOREST_CLIENT_STATUS["CODE_ACTIVE"]
            )
            if self.forest_client_number_exists(forest_client_find_result)
            else False
        )

    def get_forest_client(
        self, forest_client_find_result: List[ForestClientValidatorResponse]
    ) -> Union[ForestClientValidatorResponse, None]:
        return (
            forest_client_find_result[0]
            if self.forest_client_number_exists(forest_client_find_result)
            else None
        )
