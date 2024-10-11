import logging
import os
import sys
from typing import List, Optional, Union

import pytest
import testcontainers.compose
from Crypto.PublicKey import RSA
from fastapi.testclient import TestClient
from mock import patch
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import api.app.database as database
import api.app.jwt_validation as jwt_validation
from api.app.constants import AppEnv, RoleType, UserType
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.main import app
from api.app.models.model import (FamAccessControlPrivilege,
                                  FamApplicationAdmin, FamUser)
from api.app.repositories.access_control_privilege_repository import \
    AccessControlPrivilegeRepository
from api.app.repositories.application_admin_repository import \
    ApplicationAdminRepository
from api.app.repositories.application_repository import ApplicationRepository
from api.app.repositories.forest_client_repository import \
    ForestClientRepository
from api.app.repositories.role_repository import RoleRepository
from api.app.repositories.user_repository import UserRepository
from api.app.routers.router_guards import get_verified_target_user
from api.app.schemas.schemas import (FamAccessControlPrivilegeCreateDto,
                                     FamUserDto, Requester, TargetUser)
from api.app.services.access_control_privilege_service import \
    AccessControlPrivilegeService
from api.app.services.admin_user_access_service import AdminUserAccessService
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.forest_client_service import ForestClientService
from api.app.services.permission_audit_service import PermissionAuditService
from api.app.services.role_service import RoleService
from api.app.services.user_service import UserService
from tests.constants import (TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
                             TEST_CREATOR, TEST_DUMMY_COGNITO_USER_ID,
                             TEST_FOM_DEV_REVIEWER_ROLE_ID,
                             TEST_FOM_DEV_SUBMITTER_ROLE_ID,
                             TEST_FOM_TEST_REVIEWER_ROLE_ID,
                             TEST_FOM_TEST_SUBMITTER_ROLE_ID,
                             TEST_NEW_IDIR_USER)

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


@pytest.fixture(scope="function")
def setup_new_user(user_repo: UserRepository, db_pg_session: Session):
    """
    New user setup for testing using repository.
    The fixture returns a function to be called with new user created based on
        user_type, user_name and optionally if need to add cognito_user_id.
    """

    def _setup_new_user(
        user_type: UserType, user_name, user_guid, cognito_user_id: Optional[str] = None
    ) -> FamUser:
        new_user_create = FamUserDto(
            **{
                "user_type_code": user_type,
                "user_name": user_name,
                "user_guid": user_guid,
                "create_user": TEST_CREATOR,
            }
        )

        fam_user = user_repo.create_user(new_user_create)
        if cognito_user_id is not None:
            # SqlAlchemy is a bit strange, need to use `.query()` to do the
            # update() and query() again in order to get correct updated entity
            # from session.
            db_pg_session.query(FamUser).filter(
                FamUser.user_id == fam_user.user_id
            ).update({FamUser.cognito_user_id: cognito_user_id})

            fam_user = (
                db_pg_session.query(FamUser)
                .filter(FamUser.user_id == fam_user.user_id)
                .one()
            )

        return fam_user

    return _setup_new_user


@pytest.fixture(scope="function")
def new_idir_requester(setup_new_user) -> Requester:
    """
    Setup a new IDIR type user in test db session and return as a schema object.
    Convenient setup for some test scenarios.
    Returns:
        new user schema object created from test db session.
    """
    new_user = setup_new_user(
        TEST_NEW_IDIR_USER.user_type_code,
        TEST_NEW_IDIR_USER.user_name,
        TEST_NEW_IDIR_USER.user_guid,
        TEST_DUMMY_COGNITO_USER_ID
    )

    requester = Requester.model_validate(
		new_user.__dict__
	)
    return requester


@pytest.fixture(scope="function")
def setup_new_app_admin(application_admin_repo: ApplicationAdminRepository):
    """
    Conveniently setup new APP_ADMIN user for testing using repository.
    The fixture returns a function to be called with new app admin created
        based on application_id the user (user_id) is intended to administer.
    """

    def __setup_new_app_admin(user_id: int, application_id: int) -> FamApplicationAdmin:
        new_fam_admin = application_admin_repo.create_application_admin(
            application_id,
            user_id,
            TEST_CREATOR,
        )
        return new_fam_admin

    return __setup_new_app_admin


@pytest.fixture(scope="function")
def setup_new_fom_delegated_admin(
    access_control_privilege_repo: AccessControlPrivilegeRepository,
    role_service: RoleService,
):
    """
    Conveniently setup new "FOM" DELEGATED_ADMIN user for testing.
    The fixture returns a function to be called with new FOM (env) delegated
        admin created based on environment and role the user (user_id) is
        intended to administer. Note, this is only for FOM application with
        known roles.
    """

    def __setup_new_fom_delegated_admin(
        user_id: int,
        role_type: RoleType,
        env: Union[
            AppEnv.APP_ENV_TYPE_DEV, AppEnv.APP_ENV_TYPE_TEST
        ],  # note, do not pass PROD.
        forest_client_numbers: Optional[List[str]] = None,
    ) -> List[FamAccessControlPrivilege]:
        if role_type is RoleType.ROLE_TYPE_CONCRETE:
            delegated_admin_create = FamAccessControlPrivilegeCreateDto(
                **{
                    "user_id": user_id,
                    "role_id": (
                        TEST_FOM_DEV_REVIEWER_ROLE_ID
                        if env is AppEnv.APP_ENV_TYPE_DEV
                        else TEST_FOM_TEST_REVIEWER_ROLE_ID
                    ),
                    "create_user": TEST_CREATOR,
                }
            )
            return [
                access_control_privilege_repo.create_access_control_privilege(
                    delegated_admin_create
                )
            ]
        else:
            fom_submitter_role_id = (
                TEST_FOM_DEV_SUBMITTER_ROLE_ID
                if env is AppEnv.APP_ENV_TYPE_DEV
                else TEST_FOM_TEST_SUBMITTER_ROLE_ID
            )
            fom_parent_role = role_service.get_role_by_id(fom_submitter_role_id)
            delegated_admin_privileges = []
            for forest_client_number in forest_client_numbers:
                child_role = role_service.find_or_create_forest_client_child_role(
                    forest_client_number, fom_parent_role, TEST_CREATOR
                )
                delegated_admin_create = FamAccessControlPrivilegeCreateDto(
                    **{
                        "user_id": user_id,
                        "role_id": child_role.role_id,
                        "create_user": TEST_CREATOR,
                    }
                )
                delegated_admin_privileges.append(
                    access_control_privilege_repo.create_access_control_privilege(
                        delegated_admin_create
                    )
                )
            return delegated_admin_privileges

    return __setup_new_fom_delegated_admin


@pytest.fixture(scope="function")
def override_get_verified_target_user(test_client_fixture):
    # mock the return result for idim validation of the target user

    def _override_get_verified_target_user(
        mocked_data=TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
    ):
        app = test_client_fixture.app
        app.dependency_overrides[get_verified_target_user] = lambda: TargetUser(
            **mocked_data
        )

    return _override_get_verified_target_user


@pytest.fixture(scope="function", autouse=True)
def mock_forest_client_integration_service():
    # Mocked dependency class object
    with patch(
        "api.app.integration.forest_client_integration.ForestClientIntegrationService",
        autospec=True,
    ) as m:
        yield m.return_value  # Very important to get instance of mocked class.


def to_mocked_target_user(rbody: dict):
    return TargetUser(**rbody)


def override_get_rsa_key_method():
    return override_get_rsa_key


def override_get_rsa_key(token):
    global public_rsa_key
    return public_rsa_key


def override_get_rsa_key_method_none():
    return override_get_rsa_key_none


def override_get_rsa_key_none(kid):
    return None


@pytest.fixture(scope="function")
def user_repo(db_pg_session: Session):
    return UserRepository(db_pg_session)


@pytest.fixture(scope="function")
def role_repo(db_pg_session: Session):
    return RoleRepository(db_pg_session)


@pytest.fixture(scope="function")
def application_repo(db_pg_session: Session):
    return ApplicationRepository(db_pg_session)


@pytest.fixture(scope="function")
def forest_client_repo(db_pg_session: Session):
    return ForestClientRepository(db_pg_session)


@pytest.fixture(scope="function")
def application_admin_repo(db_pg_session: Session):
    return ApplicationAdminRepository(db_pg_session)


@pytest.fixture(scope="function")
def access_control_privilege_repo(db_pg_session: Session):
    return AccessControlPrivilegeRepository(db_pg_session)


@pytest.fixture(scope="function")
def user_service(db_pg_session: Session):
    return UserService(db_pg_session)


@pytest.fixture(scope="function")
def role_service(db_pg_session: Session):
    return RoleService(db_pg_session)


@pytest.fixture(scope="function")
def forest_client_service(db_pg_session: Session):
    return ForestClientService(db_pg_session)


@pytest.fixture(scope="function")
def application_admin_service(db_pg_session: Session):
    return ApplicationAdminService(db_pg_session)


@pytest.fixture(scope="function")
def access_control_privilege_service(db_pg_session: Session):
    return AccessControlPrivilegeService(db_pg_session)


@pytest.fixture(scope="function")
def admin_user_access_service(db_pg_session: Session):
    return AdminUserAccessService(db_pg_session)


@pytest.fixture(scope="function")
def forest_client_integration_service():
    return ForestClientIntegrationService()


@pytest.fixture(scope="function")
def permission_audit_service(db_pg_session: Session):
    return PermissionAuditService(db_pg_session)