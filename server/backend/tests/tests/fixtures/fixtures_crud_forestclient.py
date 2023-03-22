import logging
from typing import Dict, Generator, Iterator, Union

import pytest
import tests.tests.test_constants as testConstants
from api.app.models import model

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def forest_client_dict() -> Iterator[Dict[str, str]]:
    fc_dict = {
        "forest_client_number" : "00001101",
        #"client_name": "acme forestry",
        "create_user": testConstants.FAM_PROXY_API_USER
        # TODO: should duplicate this pattern all through the tests for population of create_user, and think about making it the default way this field is populated in the app for all tables.
    }
    yield fc_dict


@pytest.fixture(scope="function")
def forest_client_model(
        forest_client_dict: Iterator[Dict[str, str]]) -> model.FamForestClient:
    fc_model = model.FamForestClient(**forest_client_dict)
    yield fc_model
