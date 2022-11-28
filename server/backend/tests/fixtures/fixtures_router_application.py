import logging
import pytest
import starlette.testclient
import sqlalchemy.orm
from typing import Dict, Any, Union

from api.app.crud import crud_application as crud_application


LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def testApplication_fixture(
        testClient_fixture: starlette.testclient.TestClient,
        dbSession_famApplication: sqlalchemy.orm.session.Session):
    # using the fixture below to populate the database with data
    # committing here as the testClient_fixture will generate its
    # own session, so need to commit the data for the session to
    # be able to see the data.
    dbSession_famApplication.commit()
    LOGGER.debug("got here")
    yield testClient_fixture

    dbSession_famApplication.rollback()


@pytest.fixture(scope="function")
def application_roles(
        dbSession_famApplication: sqlalchemy.orm.session.Session,
        testClient_fixture: starlette.testclient.TestClient,
        applicationData1: Dict[str, Any]) -> \
        Dict[str, Union[starlette.testclient.TestClient, int]]:
    db = dbSession_famApplication
    # have to commit so that the session spun up by the client can see the data
    db.commit()
    # get the app id and pass on
    app = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    LOGGER.debug(f"app: {app}")
    app_id = app.application_id

    yield {"client": testClient_fixture, "app_id": app_id}
    # TODO: verify that the rollback works
    db.rollback()
