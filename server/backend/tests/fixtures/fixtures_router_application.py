import logging
import pytest
import starlette.testclient
import sqlalchemy.orm
from typing import Dict, Any, Union, Iterator

from api.app.crud import crud_application as crud_application


LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def client_application(
        test_client_fixture: starlette.testclient.TestClient,
        dbsession_application: sqlalchemy.orm.session.Session):
    # using the fixture below to populate the database with data
    # committing here as the test_client_fixture will generate its
    # own session, so need to commit the data for the session to
    # be able to see the data.
    dbsession_application.commit()
    LOGGER.debug("got here")
    yield test_client_fixture

    dbsession_application.rollback()


@pytest.fixture(scope="function")
def application_roles(
        dbsession_application_concrete_role: sqlalchemy.orm.session.Session,
        test_client_fixture: starlette.testclient.TestClient,
        application_dict: Dict[str, Any]) -> \
        Iterator[Dict[str, Union[starlette.testclient.TestClient, int]]]:
    db = dbsession_application_concrete_role
    # have to commit so that the session spun up by the client can see the data
    db.commit()
    # get the app id and pass on
    app = crud_application.get_application_by_name(
        db=db, application_name=application_dict["application_name"]
    )
    LOGGER.debug(f"app: {app}")
    app_id = app.application_id

    yield {"client": test_client_fixture, "app_id": app_id}
    # TODO: verify that the rollback works
    db.rollback()


@pytest.fixture(scope="function")
def application_role_assignment(
        dbsession_application_with_role_user_assignment,
        test_client_fixture,
        application_dict,
        concrete_role_dict,
        user_data_dict):
    # TODO: concrete_role_dict and userData not used yet, but should be part
    #       of the assertions as that is the test user and role user to be
    #       used for the role assignment
    db = dbsession_application_with_role_user_assignment
    # have to commit the session for the api to be able to see it as each request
    # uses its own session
    db.commit()
    app = crud_application.get_application_by_name(
        db=db, application_name=application_dict["application_name"]
    )
    app_id = app.application_id
    LOGGER.debug(f"app_id: {app_id}")
    yield {'client': test_client_fixture, 'app_id': app_id}
    db.rollback()
