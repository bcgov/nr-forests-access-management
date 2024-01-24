import logging
import pytest
from sqlalchemy.exc import IntegrityError

from api.app.repositories.forest_client_repository import ForestClientRepository
from tests.constants import (
    TEST_FOERST_CLIENT_CREATE,
    TEST_NON_EXIST_FOREST_CLIENT_NUMBER,
    ERROR_VOLIATE_UNIQUE_CONSTRAINT,
)


LOGGER = logging.getLogger(__name__)


def test_get_forest_client_by_mumber(forest_client_repo: ForestClientRepository):
    # get non exist forest client
    found_forest_client = forest_client_repo.get_forest_client_by_number(
        TEST_NON_EXIST_FOREST_CLIENT_NUMBER
    )
    assert found_forest_client is None

    # create a new forest client
    new_forest_client = forest_client_repo.create_forest_client(
        TEST_FOERST_CLIENT_CREATE
    )
    assert (
        new_forest_client.forest_client_number
        == TEST_FOERST_CLIENT_CREATE.forest_client_number
    )
    # get the new created forest client
    found_forest_client = forest_client_repo.get_forest_client_by_number(
        TEST_FOERST_CLIENT_CREATE.forest_client_number
    )
    assert (
        found_forest_client.forest_client_number
        == TEST_FOERST_CLIENT_CREATE.forest_client_number
    )


def test_create_forest_client(forest_client_repo: ForestClientRepository):
    # create a new forest client
    new_forest_client = forest_client_repo.create_forest_client(
        TEST_FOERST_CLIENT_CREATE
    )
    assert (
        new_forest_client.forest_client_number
        == TEST_FOERST_CLIENT_CREATE.forest_client_number
    )
    # verify the new created forest client
    found_forest_client = forest_client_repo.get_forest_client_by_number(
        TEST_FOERST_CLIENT_CREATE.forest_client_number
    )
    assert found_forest_client.client_number_id == new_forest_client.client_number_id
    assert (
        found_forest_client.forest_client_number
        == new_forest_client.forest_client_number
    )

    # create a duplicate forest client
    with pytest.raises(IntegrityError) as e:
        forest_client_repo.create_forest_client(TEST_FOERST_CLIENT_CREATE)
    assert str(e.value).find(ERROR_VOLIATE_UNIQUE_CONSTRAINT) != -1