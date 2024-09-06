import logging

from api.app.schemas import FamForestClientCreateSchema
from api.app.crud import crud_forest_client
from api.app.models import model as models
from sqlalchemy.orm import Session
from testspg.constants import TEST_CREATOR

LOGGER = logging.getLogger(__name__)

TEST_FOERST_CLIENT_DATA = {
    "forest_client_number": "00000010",
    "create_user": TEST_CREATOR,
}
TEST_NON_EXIST_FOREST_CLIENT_NUMBER = "99999999"


def test_create_forest_client(db_pg_session: Session):
    new_forest_client = crud_forest_client.create_forest_client(
        FamForestClientCreateSchema(**TEST_FOERST_CLIENT_DATA), db_pg_session
    )
    assert (
        new_forest_client.forest_client_number
        == TEST_FOERST_CLIENT_DATA["forest_client_number"]
    )

    found_forest_client = crud_forest_client.get_forest_client(
        db_pg_session, TEST_FOERST_CLIENT_DATA["forest_client_number"]
    )
    assert found_forest_client.client_number_id == new_forest_client.client_number_id
    assert (
        found_forest_client.forest_client_number
        == new_forest_client.forest_client_number
    )


def test_get_forest_client(db_pg_session: Session):
    # get non exist forest client
    found_forest_client = crud_forest_client.get_forest_client(
        db_pg_session, TEST_NON_EXIST_FOREST_CLIENT_NUMBER
    )
    assert found_forest_client is None

    # create a new forest client
    new_forest_client = crud_forest_client.create_forest_client(
        FamForestClientCreateSchema(**TEST_FOERST_CLIENT_DATA), db_pg_session
    )
    assert (
        new_forest_client.forest_client_number
        == TEST_FOERST_CLIENT_DATA["forest_client_number"]
    )
    # get the new created forest client
    found_forest_client = crud_forest_client.get_forest_client(
        db_pg_session, TEST_FOERST_CLIENT_DATA["forest_client_number"]
    )
    assert (
        found_forest_client.forest_client_number
        == TEST_FOERST_CLIENT_DATA["forest_client_number"]
    )


def test_find_or_create(db_pg_session: Session):
    initial_all = db_pg_session.query(models.FamForestClient).all()
    # verify the target forest client not exists
    found_forest_client = crud_forest_client.get_forest_client(
        db_pg_session, TEST_FOERST_CLIENT_DATA["forest_client_number"]
    )
    assert found_forest_client is None
    # find or create with an non exists forest client
    crud_forest_client.find_or_create(
        db_pg_session,
        TEST_FOERST_CLIENT_DATA["forest_client_number"],
        TEST_FOERST_CLIENT_DATA["create_user"],
    )
    # verify can find that forest client now
    found_forest_client = crud_forest_client.get_forest_client(
        db_pg_session, TEST_FOERST_CLIENT_DATA["forest_client_number"]
    )
    assert found_forest_client is not None
    after_add_all = db_pg_session.query(models.FamForestClient).all()
    assert len(after_add_all) == len(initial_all) + 1

    # find or create with an existing forest client
    crud_forest_client.find_or_create(
        db_pg_session,
        TEST_FOERST_CLIENT_DATA["forest_client_number"],
        TEST_FOERST_CLIENT_DATA["create_user"],
    )
    all_forest_clients = db_pg_session.query(models.FamForestClient).all()
    # verify no new forest client add
    assert len(all_forest_clients) == len(after_add_all)
