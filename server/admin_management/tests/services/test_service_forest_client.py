import logging
from sqlalchemy.orm import Session

from api.app.models.model import FamForestClient
from api.app.services.forest_client_service import ForestClientService

from tests.constants import TEST_FOERST_CLIENT_CREATE


LOGGER = logging.getLogger(__name__)


def test_find_or_create(
    forest_client_service: ForestClientService, db_pg_session: Session
):
    # verify the new forest client not exists
    found_forest_client = forest_client_service.get_forest_client_by_number(
        TEST_FOERST_CLIENT_CREATE.forest_client_number
    )
    assert found_forest_client is None
    initial_all = db_pg_session.query(FamForestClient).all()

    # create the newe forest client
    forest_client_service.find_or_create(
        TEST_FOERST_CLIENT_CREATE.forest_client_number,
        TEST_FOERST_CLIENT_CREATE.create_user,
    )
    # verify the forest client number can be found now
    found_forest_client = forest_client_service.get_forest_client_by_number(
        TEST_FOERST_CLIENT_CREATE.forest_client_number
    )
    assert found_forest_client is not None
    after_add_all = db_pg_session.query(FamForestClient).all()
    assert len(after_add_all) == len(initial_all) + 1

    # find or create with an existing forest client
    forest_client_service.find_or_create(
        TEST_FOERST_CLIENT_CREATE.forest_client_number,
        TEST_FOERST_CLIENT_CREATE.create_user,
    )
    all_forest_clients = db_pg_session.query(FamForestClient).all()
    # verify no new forest client add
    assert len(all_forest_clients) == len(after_add_all)
