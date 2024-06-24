import logging
import os
import sys
from typing import List

import pytest
import starlette
import testcontainers.compose
from Crypto.PublicKey import RSA
from fastapi.testclient import TestClient
from jose import jwt
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import api.app.database as database
import api.app.jwt_validation as jwt_validation
import testspg.jwt_utils as jwt_utils
from api.app.constants import (COGNITO_USERNAME_KEY,
                               ERROR_CODE_TERMS_CONDITIONS_REQUIRED)
from api.app.crud import crud_utils
from api.app.main import apiPrefix, app
from api.app.routers.router_guards import (
    enforce_bceid_terms_conditions_guard, get_current_requester,
    get_verified_target_user)
from api.app.schemas import Requester, TargetUser
from testspg.constants import (ACCESS_GRANT_FOM_DEV_CR_IDIR,
                               FOM_DEV_ADMIN_ROLE, FOM_TEST_ADMIN_ROLE)

LOGGER = logging.getLogger(__name__)
# the folder contains test docker-compose.yml, ours in the root directory
COMPOSE_PATH = os.path.join(os.path.dirname(__file__), "../../../")
COMPOSE_FILE_NAME = "docker-compose-testcontainer.yml"


@pytest.fixture(scope="session")
def db_pg_container():
    # LOGGER.debug("db_pg_container() commented out for local testing")
    compose = testcontainers.compose.DockerCompose(
        COMPOSE_PATH, compose_file_name=COMPOSE_FILE_NAME
    )
    compose.start()
    # NGINX is set to start only when flyway is complete
    compose.wait_for("http://localhost:8181")
    yield compose
    compose.stop()


@pytest.fixture(scope="session")
def db_pg_connection(db_pg_container):

    engine = create_engine(
        "postgresql+psycopg2://"
        + f"{os.environ.get('POSTGRES_USER')}:"
        + f"{os.environ.get('POSTGRES_PASSWORD')}@"
        + f"{os.environ.get('POSTGRES_HOST')}:"
        f"{os.environ.get('POSTGRES_PORT')}/"
        f"{os.environ.get('POSTGRES_DB')}"
    )

    session_local = sessionmaker(bind=engine)
    test_db = session_local()

    yield test_db
    test_db.close()


@pytest.fixture(scope="function")
def db_pg_session(db_pg_connection: Session):
    yield db_pg_connection
    db_pg_connection.rollback()


@pytest.fixture(scope="function")
def test_client_fixture_unit() -> TestClient:

    app.dependency_overrides[database.get_db] = lambda: UnifiedAlchemyMagicMock(data=[])

    return TestClient(app)


@pytest.fixture(scope="function")
def test_client_fixture(db_pg_session) -> TestClient:
    """returns a requests object of the current app,
    with the objects defined in the model created in it.

    :rtype: starlette.testclient
    """
    # reset to default database which points to postgres container
    app.dependency_overrides[database.get_db] = lambda: db_pg_session

    yield TestClient(app)

    # reset other dependency override back to app default in each test
    # during test case teardown.
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def test_rsa_key():

    new_key = RSA.generate(2048)
    global public_rsa_key
    public_rsa_key = new_key.publickey().exportKey("PEM")

    app.dependency_overrides[jwt_validation.get_rsa_key_method] = (
        override_get_rsa_key_method
    )

    return new_key.exportKey("PEM")


@pytest.fixture(scope="function")
def test_rsa_key_missing():

    new_key = RSA.generate(2048)
    global public_rsa_key
    public_rsa_key = new_key.publickey().exportKey("PEM")

    app.dependency_overrides[jwt_validation.get_rsa_key_method] = (
        override_get_rsa_key_method_none
    )

    return new_key.exportKey("PEM")


def override_get_rsa_key_method():
    return override_get_rsa_key


def override_get_rsa_key(kid):
    global public_rsa_key
    return public_rsa_key


def override_get_rsa_key_method_none():
    return override_get_rsa_key_none


def override_get_rsa_key_none(kid):
    return None


@pytest.fixture(scope="function")
def fom_dev_access_admin_token(test_rsa_key):
    access_roles = [FOM_DEV_ADMIN_ROLE]
    return jwt_utils.create_jwt_token(test_rsa_key, access_roles)


@pytest.fixture(scope="function")
def fom_test_access_admin_token(test_rsa_key):
    access_roles = [FOM_TEST_ADMIN_ROLE]
    return jwt_utils.create_jwt_token(test_rsa_key, access_roles)


@pytest.fixture(scope="function")
def get_current_requester_by_token(db_pg_session):
    """
    Convenient fixture to get current requester from token (retrieved from database setup).
    The fixture returns a function to be called based on access_token's ["username"]
        , which is the user's cognito_user_id.

    Note, the returned function is an 'async'.
        To be able to use the returned function from Pytest, please mark the test
        as '@pytest.mark.asyncio' and use 'async def' for the test with 'await'
        call to the fixture.
        (Although it is strange the outer function is not async but it is
         currently how Pytest can work with async from fixture.)
    """

    async def _get_current_requester_by_token(access_token: str) -> Requester:

        claims = jwt.get_unverified_claims(access_token)
        requester = await get_current_requester(
            db=db_pg_session,
            access_roles=jwt_validation.get_access_roles(claims),
            request_cognito_user_id=claims[COGNITO_USERNAME_KEY],
        )
        LOGGER.debug(f"requester: {requester}")

        return requester

    return _get_current_requester_by_token


@pytest.fixture(scope="function")
def override_get_verified_target_user(test_client_fixture):
    # mock the return result for idim validation of the target user, to avoid calling external idim-proxy
    def _override_get_verified_target_user(mocked_data=ACCESS_GRANT_FOM_DEV_CR_IDIR):
        app = test_client_fixture.app
        app.dependency_overrides[get_verified_target_user] = lambda: TargetUser(
            **mocked_data
        )

    return _override_get_verified_target_user


@pytest.fixture(scope="function")
def create_test_user_role_assignments(
    test_client_fixture, override_get_verified_target_user
):
    """
    Convenient function to assign multipe users to an application.
    :param requester_token: token to be used for the request.
                            Pass appropriate application_admin level to
                            create the users to.
    :param request_bodies: request content to create the users.
    """

    def _create_test_user_role_assignments(requester_token, request_bodies: List[dict]):
        created_users = []
        for request_body in request_bodies:
            override_get_verified_target_user(request_body)
            created_users.append(
                create_test_user_role_assignment(
                    test_client_fixture=test_client_fixture,
                    token=requester_token,
                    request_body=request_body,
                )
            )
        return created_users

    return _create_test_user_role_assignments


# helper method
# create a user role assignment used for testing
def create_test_user_role_assignment(
    test_client_fixture: starlette.testclient.TestClient, token, request_body
):
    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=request_body,
        headers=jwt_utils.headers(token),
    )
    data = response.json()
    return data["user_role_xref_id"]


@pytest.fixture(scope="function")
def override_enforce_bceid_terms_conditions_guard(test_client_fixture):
    # Override T&C checks based on test cases scenarios.
    def _override_enforce_bceid_terms_conditions_guard(mocked_tc_accepted=True):
        app = test_client_fixture.app
        app.dependency_overrides[
            enforce_bceid_terms_conditions_guard
        ] = lambda: (None if mocked_tc_accepted else crud_utils.raise_http_exception(
                error_code=ERROR_CODE_TERMS_CONDITIONS_REQUIRED,
                error_msg="Requires to accept terms and conditions.",
            )
        )

    return _override_enforce_bceid_terms_conditions_guard
