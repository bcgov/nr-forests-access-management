import logging

from api.app.constants import FOREST_CLIENT_STATUS
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.schemas.forest_client_integration import \
    ForestClientIntegrationSearchParmsSchema
from api.app.services.validator.forest_client_validator import (
    forest_client_active, forest_client_number_exists,
    get_forest_client_status)
from tests.constants import (TEST_FOREST_CLIENT_NUMBER,
                             TEST_INACTIVE_FOREST_CLIENT_NUMBER,
                             TEST_NON_EXIST_FOREST_CLIENT_NUMBER)

LOGGER = logging.getLogger(__name__)


def test_forest_client_number_exists(
    forest_client_integration_service: ForestClientIntegrationService,
):
    # find active forest client number
    forest_client_validator_return = (
        forest_client_integration_service.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[TEST_FOREST_CLIENT_NUMBER])
        )
    )
    # test forest_client_number_exists return true
    assert forest_client_number_exists(forest_client_validator_return) is True

    # find inactive forest client number
    forest_client_validator_return = (
        forest_client_integration_service.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[TEST_INACTIVE_FOREST_CLIENT_NUMBER])
        )
    )
    # test forest_client_number_exists return true
    assert forest_client_number_exists(forest_client_validator_return) is True

    # find non exist forest client number
    forest_client_validator_return = (
        forest_client_integration_service.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[TEST_NON_EXIST_FOREST_CLIENT_NUMBER])
        )
    )
    # test forest_client_number_exists return false
    assert forest_client_number_exists(forest_client_validator_return) is False


def test_forest_client_active(forest_client_integration_service: ForestClientIntegrationService):
    # find active forest client number
    forest_client_validator_return = (
        forest_client_integration_service.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[TEST_FOREST_CLIENT_NUMBER])
        )
    )
    # test forest_client_active return true
    assert forest_client_active(forest_client_validator_return) is True

    # find inactive forest client number
    forest_client_validator_return = (
        forest_client_integration_service.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[TEST_INACTIVE_FOREST_CLIENT_NUMBER])
        )
    )
    # test forest_client_active return false
    assert forest_client_active(forest_client_validator_return) is False

    # find non exist forest client number
    forest_client_validator_return = (
        forest_client_integration_service.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[TEST_NON_EXIST_FOREST_CLIENT_NUMBER])
        )
    )
    # test forest_client_active return false
    assert forest_client_active(forest_client_validator_return) is False


def test_get_forest_client_status(
    forest_client_integration_service: ForestClientIntegrationService,
):
    # find active forest client number
    forest_client_validator_return = (
        forest_client_integration_service.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[TEST_FOREST_CLIENT_NUMBER])
        )
    )
    # test get_forest_client_status return forest client information
    assert get_forest_client_status(
        forest_client_validator_return
    ) == FOREST_CLIENT_STATUS.get("CODE_ACTIVE")

    # find inactive forest client number
    forest_client_validator_return = (
        forest_client_integration_service.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[TEST_INACTIVE_FOREST_CLIENT_NUMBER])
        )
    )
    # test get_forest_client_status return forest client information
    assert get_forest_client_status(forest_client_validator_return) == "DAC"

    # find non exist forest client number
    forest_client_validator_return = (
        forest_client_integration_service.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[TEST_NON_EXIST_FOREST_CLIENT_NUMBER])
        )
    )
    # test get_forest_client_status return None
    assert get_forest_client_status(forest_client_validator_return) is None
