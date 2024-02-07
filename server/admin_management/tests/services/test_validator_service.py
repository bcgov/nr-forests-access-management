import logging

import pytest
from api.app.services.validator_service import ForestClientValidator
from tests.constants import (
    TEST_FOREST_CLIENT_NUMBER,
    TEST_NON_EXIST_FOREST_CLIENT_NUMBER,
    TEST_INACTIVE_FOREST_CLIENT_NUMBER,
)

LOGGER = logging.getLogger(__name__)


def test_forest_client_number_exists(forest_client_validator: ForestClientValidator):
    # find active forest client number
    forest_client_validator_return = forest_client_validator.find_forest_client_number(
        TEST_FOREST_CLIENT_NUMBER
    )
    # test forest_client_number_exists return true
    assert (
        forest_client_validator.forest_client_number_exists(
            forest_client_validator_return
        )
        is True
    )

    # find inactive forest client number
    forest_client_validator_return = forest_client_validator.find_forest_client_number(
        TEST_INACTIVE_FOREST_CLIENT_NUMBER
    )
    # test forest_client_number_exists return true
    assert (
        forest_client_validator.forest_client_number_exists(
            forest_client_validator_return
        )
        is True
    )

    # find non exist forest client number
    forest_client_validator_return = forest_client_validator.find_forest_client_number(
        TEST_NON_EXIST_FOREST_CLIENT_NUMBER
    )
    # test forest_client_number_exists return false
    assert (
        forest_client_validator.forest_client_number_exists(
            forest_client_validator_return
        )
        is False
    )


def test_forest_client_active(forest_client_validator: ForestClientValidator):
    # find active forest client number
    forest_client_validator_return = forest_client_validator.find_forest_client_number(
        TEST_FOREST_CLIENT_NUMBER
    )
    # test forest_client_active return true
    assert (
        forest_client_validator.forest_client_active(forest_client_validator_return)
        is True
    )

    # find inactive forest client number
    forest_client_validator_return = forest_client_validator.find_forest_client_number(
        TEST_INACTIVE_FOREST_CLIENT_NUMBER
    )
    # test forest_client_active return false
    assert (
        forest_client_validator.forest_client_active(forest_client_validator_return)
        is False
    )

    # find non exist forest client number
    forest_client_validator_return = forest_client_validator.find_forest_client_number(
        TEST_NON_EXIST_FOREST_CLIENT_NUMBER
    )
    # test forest_client_active return false
    assert (
        forest_client_validator.forest_client_active(forest_client_validator_return)
        is False
    )


def test_get_forest_client(forest_client_validator: ForestClientValidator):
    # find active forest client number
    forest_client_validator_return = forest_client_validator.find_forest_client_number(
        TEST_FOREST_CLIENT_NUMBER
    )
    # test get_forest_client return forest client information
    assert (
        forest_client_validator.get_forest_client(forest_client_validator_return)
        == forest_client_validator_return[0]
    )

    # find inactive forest client number
    forest_client_validator_return = forest_client_validator.find_forest_client_number(
        TEST_INACTIVE_FOREST_CLIENT_NUMBER
    )
    # test get_forest_client return forest client information
    assert (
        forest_client_validator.get_forest_client(forest_client_validator_return)
        == forest_client_validator_return[0]
    )

    # find non exist forest client number
    forest_client_validator_return = forest_client_validator.find_forest_client_number(
        TEST_NON_EXIST_FOREST_CLIENT_NUMBER
    )
    # test get_forest_client return None
    assert (
        forest_client_validator.get_forest_client(forest_client_validator_return)
        is None
    )
