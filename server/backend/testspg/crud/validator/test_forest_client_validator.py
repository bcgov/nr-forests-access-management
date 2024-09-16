import logging

import pytest
from api.app.crud.validator.forest_client_validator import (
    forest_client_active, forest_client_number_exists,
    get_forest_client_status)
from mock import patch
from testspg.constants import (FC_NUMBER_EXISTS_ACTIVE_00000001,
                               FC_NUMBER_EXISTS_DEACTIVATED,
                               FC_NUMBER_EXISTS_DECEASED,
                               FC_NUMBER_EXISTS_RECEIVERSHIP,
                               FC_NUMBER_EXISTS_SUSPENDED,
                               FC_NUMBER_LEN_TOO_SHORT, FC_NUMBER_NOT_EXISTS)

from server.backend.api.app.integration.forest_client_integration import \
    ForestClientIntegrationService

LOGGER = logging.getLogger(__name__)


# Override this.
sample_forest_client_return = [
    {
        "clientNumber": FC_NUMBER_EXISTS_ACTIVE_00000001,
        "clientName": "Testing Org",
        "clientStatusCode": "some_api_client_status_code",
        "clientTypeCode": "I",
        "acronyms": [],
    }
]


@pytest.fixture(scope="function", autouse=True)
def mock_forest_client():
    # Mocked dependency class object
    with patch(
        "api.app.integration.forest_client.forest_client.ForestClientService",
        autospec=True,
    ) as m:
        yield m.return_value  # Very important to get instance of mocked class.


@pytest.fixture(scope="function")
def forest_client_integration_service():
    return ForestClientIntegrationService()


def __to_mock_forest_client_return(forest_client_number, api_client_status_code):
    return (
        [
            {
                **sample_forest_client_return[0],
                "clientNumber": forest_client_number,
                "clientStatusCode": api_client_status_code,
            }
        ]
        if api_client_status_code is not None
        else []
    )


@pytest.mark.parametrize(
    "client_id_to_test, expcted_result",
    [
        (FC_NUMBER_LEN_TOO_SHORT, {"api_client_status_code": None, "exists": False}),
        (FC_NUMBER_NOT_EXISTS, {"api_client_status_code": None, "exists": False}),
        (
            FC_NUMBER_EXISTS_ACTIVE_00000001,
            {"api_client_status_code": "ACT", "exists": True},
        ),
        (
            FC_NUMBER_EXISTS_DEACTIVATED,
            {"api_client_status_code": "DAC", "exists": True},
        ),
        (FC_NUMBER_EXISTS_DECEASED, {"api_client_status_code": "DEC", "exists": True}),
        (
            FC_NUMBER_EXISTS_RECEIVERSHIP,
            {"api_client_status_code": "REC", "exists": True},
        ),
        (FC_NUMBER_EXISTS_SUSPENDED, {"api_client_status_code": "SPN", "exists": True}),
    ],
)
def test_forest_client_number_exists(
    client_id_to_test,
    expcted_result,
    mock_forest_client,
    forest_client_integration_service,
):
    mock_forest_client.find_by_client_number.return_value = (
        __to_mock_forest_client_return(
            client_id_to_test,
            expcted_result["api_client_status_code"],
        )
    )

    # find forest client number
    forest_client_search_return = (
        forest_client_integration_service.find_by_client_number(client_id_to_test)
    )
    # test forest_client_number_exists return true
    assert (
        forest_client_number_exists(forest_client_search_return)
        is expcted_result["exists"]
    )


@pytest.mark.parametrize(
    "client_id_to_test, expcted_result",
    [
        (FC_NUMBER_LEN_TOO_SHORT, {"api_client_status_code": None, "is_active": False}),
        (FC_NUMBER_NOT_EXISTS, {"api_client_status_code": None, "is_active": False}),
        (
            FC_NUMBER_EXISTS_ACTIVE_00000001,
            {"api_client_status_code": "ACT", "is_active": True},
        ),
        (
            FC_NUMBER_EXISTS_DEACTIVATED,
            {"api_client_status_code": "DAC", "is_active": False},
        ),
        (
            FC_NUMBER_EXISTS_DECEASED,
            {"api_client_status_code": "DEC", "is_active": False},
        ),
        (
            FC_NUMBER_EXISTS_RECEIVERSHIP,
            {"api_client_status_code": "REC", "is_active": False},
        ),
        (
            FC_NUMBER_EXISTS_SUSPENDED,
            {"api_client_status_code": "SPN", "is_active": False},
        ),
    ],
)
def test_forest_client_active(
    client_id_to_test,
    expcted_result,
    mock_forest_client,
    forest_client_integration_service,
):
    mock_forest_client.find_by_client_number.return_value = (
        __to_mock_forest_client_return(
            client_id_to_test,
            expcted_result["api_client_status_code"],
        )
    )

    # find forest client number
    forest_client_search_return = (
        forest_client_integration_service.find_by_client_number(client_id_to_test)
    )

    assert (
        forest_client_active(forest_client_search_return)
        is expcted_result["is_active"]
    )


@pytest.mark.parametrize(
    "client_id_to_test, expcted_result",
    [
        (FC_NUMBER_LEN_TOO_SHORT, {"api_client_status_code": None}),
        (FC_NUMBER_NOT_EXISTS, {"api_client_status_code": None}),
        (FC_NUMBER_EXISTS_ACTIVE_00000001, {"api_client_status_code": "ACT"}),
        (FC_NUMBER_EXISTS_DEACTIVATED, {"api_client_status_code": "DAC"}),
        (FC_NUMBER_EXISTS_DECEASED, {"api_client_status_code": "DEC"}),
        (FC_NUMBER_EXISTS_RECEIVERSHIP, {"api_client_status_code": "REC"}),
        (FC_NUMBER_EXISTS_SUSPENDED, {"api_client_status_code": "SPN"}),
    ],
)
def test_get_forest_client_status(
    client_id_to_test,
    expcted_result,
    mock_forest_client,
    forest_client_integration_service,
):
    mock_forest_client.find_by_client_number.return_value = (
        __to_mock_forest_client_return(
            client_id_to_test,
            expcted_result["api_client_status_code"],
        )
    )

    # find forest client number
    forest_client_search_return = (
        forest_client_integration_service.find_by_client_number(client_id_to_test)
    )

    # test get_forest_client_status return forest client information
    assert (
        get_forest_client_status(forest_client_search_return)
        == expcted_result["api_client_status_code"]
    )
