import os
import sys
from sqlalchemy.orm import Session
import logging
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from api.app.crud import crud_application
import api.app.schemas as schemas
import api.app.constants as constants


LOGGER = logging.getLogger(__name__)

TEST_APPLICATION_NAME_NOT_FOUND = "NOT_FOUND"
TEST_APPLICATION_ID_NOT_FOUND = 0

TEST_APPLICATION_NAME_FAM = "FAM"
TEST_APPLICATION_ID_FAM = 1
TEST_APPLICATION_ROLE_ID_FAM = 1

TEST_APPLICATION_NAME_FOM_DEV = "FOM_DEV"
TEST_APPLICATION_ID_FOM_DEV = 2
TEST_APPLICATION_ROLES_FOM_DEV = ["FOM_SUBMITTER", "FOM_REVIEWER"]
TEST_APPLICATION_ROLE_ID_FOM_DEV = 3

NEW_APPLICATION = {
    "application_name": "TEST_APP_DEV",
    "application_description": "A testing application",
    "app_environment": constants.AppEnv.APP_ENV_TYPE_DEV,
    "create_user": constants.FAM_PROXY_API_USER,
    "create_date": datetime.datetime.now(),
    "update_user": "Tester",
    "update_date": datetime.datetime.now(),
}


def test_get_applications(dbPgSession: Session):
    apps = crud_application.get_applications(db=dbPgSession)
    assert len(apps) == 7
    for app in apps:
        assert hasattr(app, "application_id")
        assert hasattr(app, "application_name")
        assert hasattr(app, "application_description")
        assert hasattr(app, "create_user")
        assert hasattr(app, "create_date")
        assert hasattr(app, "update_user")
        assert hasattr(app, "update_date")
        assert hasattr(app, "app_environment")

    assert apps[0].application_name == TEST_APPLICATION_NAME_FAM
    assert apps[1].application_name == TEST_APPLICATION_NAME_FOM_DEV
    assert apps[1].app_environment == "DEV"


def test_get_applications_by_granted_apps(dbPgSession: Session):
    # Test Accss Roles: FAM_ACCESS_ADMIN only
    access_roles_fam_only = ["FAM_ACCESS_ADMIN"]
    LOGGER.debug("Testing 'get_applications_by_granted_apps' with Accss Roles:" +
                 f"{access_roles_fam_only}")
    apps = crud_application.get_applications_by_granted_apps(
        db=dbPgSession, access_roles=access_roles_fam_only
    )
    assert len(apps) == 1
    assert apps[0].application_name == TEST_APPLICATION_NAME_FAM

    # Test Accss Roles: FOM_DEV_ACCESS_ADMIN only
    access_roles_fom_dev_only = ["FOM_DEV_ACCESS_ADMIN"]
    LOGGER.debug("Testing 'get_applications_by_granted_apps' with Accss Roles:" +
                 f"{access_roles_fom_dev_only}...")
    apps = crud_application.get_applications_by_granted_apps(
        db=dbPgSession, access_roles=access_roles_fom_dev_only
    )
    assert len(apps) == 1
    assert apps[0].application_name == "FOM_DEV"

    # Test Accss Roles: both FAM_ACCESS_ADMIN and FOM_DEV_ACCESS_ADMIN
    access_roles_fam_fom_dev = ["FAM_ACCESS_ADMIN", "FOM_DEV_ACCESS_ADMIN"]
    LOGGER.debug("Testing 'get_applications_by_granted_apps' with Accss Roles:" +
                 f"{access_roles_fam_fom_dev}...")
    apps = crud_application.get_applications_by_granted_apps(
        db=dbPgSession, access_roles=access_roles_fam_fom_dev
    )
    assert len(apps) == 2
    assert len([app for app in apps if app.application_name == "FAM"]) == 1
    assert len([app for app in apps if app.application_name == "FOM_DEV"]) == 1
    assert len([app for app in apps if app.application_name == "FOM_TEST"]) == 0

    # Test Accss Roles: on NO_APP_ACCESS_ADMIN
    access_roles_no_app = ["NO_APP_ACCESS_ADMIN"]
    LOGGER.debug("Testing 'get_applications_by_granted_apps' with Accss Roles:" +
                 f"{access_roles_no_app}...")
    apps = crud_application.get_applications_by_granted_apps(
        db=dbPgSession, access_roles=access_roles_no_app
    )
    # Shold have empty apps result.
    assert len(apps) == 0
    assert len([app for app in apps if app.application_name == "FAM"]) == 0
    assert len([app for app in apps if app.application_name == "FOM_DEV"]) == 0
    assert len([app for app in apps if app.application_name == "FOM_TEST"]) == 0


def test_get_application(dbPgSession: Session):
    apps = crud_application.get_applications(db=dbPgSession)
    assert len(apps) > 1

    for app in apps:
        app_by_id = crud_application.get_application(
            db=dbPgSession, application_id=app.application_id
        )
        assert app_by_id.application_id == app.application_id

    app_by_id = crud_application.get_application(
        db=dbPgSession, application_id=TEST_APPLICATION_ID_FAM
    )
    assert app_by_id.application_id == TEST_APPLICATION_ID_FAM
    assert app_by_id.application_name == TEST_APPLICATION_NAME_FAM

    app_by_name = crud_application.get_application(
        db=dbPgSession, application_id=TEST_APPLICATION_ID_NOT_FOUND
    )
    assert app_by_name is None


def test_get_application_by_name(dbPgSession: Session):
    apps = crud_application.get_applications(db=dbPgSession)
    assert len(apps) > 1

    for app in apps:
        app_by_name = crud_application.get_application_by_name(
            db=dbPgSession, application_name=app.application_name
        )
        assert app_by_name.application_name == app.application_name

    app_by_name = crud_application.get_application_by_name(
        db=dbPgSession, application_name=TEST_APPLICATION_NAME_FAM
    )
    assert app_by_name.application_id == TEST_APPLICATION_ID_FAM
    assert app_by_name.application_name == TEST_APPLICATION_NAME_FAM

    app_by_name = crud_application.get_application_by_name(
        db=dbPgSession, application_name=TEST_APPLICATION_NAME_NOT_FOUND
    )
    assert app_by_name is None


def test_get_application_roles(dbPgSession: Session):
    app_roles = crud_application.get_application_roles(
        db=dbPgSession, application_id=TEST_APPLICATION_ID_FOM_DEV
    )

    for app_role in app_roles:
        assert hasattr(app_role, "role_id")
        assert hasattr(app_role, "role_name")
        assert hasattr(app_role, "role_purpose")
        assert hasattr(app_role, "parent_role_id")
        assert hasattr(app_role, "application_id")
        assert hasattr(app_role, "client_number_id")
        assert hasattr(app_role, "create_user")
        assert hasattr(app_role, "create_date")
        assert hasattr(app_role, "update_user")
        assert hasattr(app_role, "update_date")
        assert hasattr(app_role, "role_type_code")
        # test the schema definitions work, will raise error if they do not
        schemas.FamApplicationRole.from_orm(app_role)

    assert len(app_roles) == 2
    assert app_roles[0].role_name == TEST_APPLICATION_ROLES_FOM_DEV[0]
    assert app_roles[0].application_id == TEST_APPLICATION_ID_FOM_DEV
    assert app_roles[0].role_type_code == "A"
    assert app_roles[1].role_name == TEST_APPLICATION_ROLES_FOM_DEV[1]
    assert app_roles[1].application_id == TEST_APPLICATION_ID_FOM_DEV
    assert app_roles[1].role_type_code == "C"

    # todo: add test for parent_role_id for abstract role, need to add a role first
    # todo: add test for client_number_id for abstract role


def test_get_application_role_assignments(dbPgSession: Session):
    # get data from a non existant app
    role_assignments = crud_application.get_application_role_assignments(
        db=dbPgSession, application_id=TEST_APPLICATION_ID_NOT_FOUND
    )
    LOGGER.debug(f"role_assignments: {role_assignments}")
    assert not role_assignments

    role_assignments = crud_application.get_application_role_assignments(
        db=dbPgSession, application_id=TEST_APPLICATION_ID_FOM_DEV
    )

    assert len(role_assignments) == 0  # initially no one is assigned with FOM_DEV roles

    # todo: add role assignment for fom dev and then verify the return

    # for role_assignment in role_assignments:
    #     # test the schema definitions work, will raise error if they do not
    #     schemas.FamApplicationUserRoleAssignmentGet.from_orm(role_assignment)


def test_get_application_id_by_role_id(dbPgSession: Session):
    app_id = crud_application.get_application_id_by_role_id(
        db=dbPgSession,
        role_id=TEST_APPLICATION_ROLE_ID_FOM_DEV
    )
    assert app_id == TEST_APPLICATION_ID_FOM_DEV

    app_id = crud_application.get_application_id_by_role_id(
        db=dbPgSession,
        role_id=TEST_APPLICATION_ROLE_ID_FOM_DEV
    )


def test_get_application_id_by_user_role_xref_id(dbPgSession: Session):
    app_id = crud_application.get_application_id_by_user_role_xref_id(
        db=dbPgSession,
        user_role_xref_id=1  # the first user in our db has role FAM admin
    )
    assert app_id == TEST_APPLICATION_ROLE_ID_FAM


def test_create_application(dbPgSession: Session):
    # verify that the data is not in the database
    app_by_name = crud_application.get_application_by_name(
        db=dbPgSession, application_name=NEW_APPLICATION["application_name"]
    )
    assert app_by_name is None

    # add the data to the database
    app_data_as_pydantic = schemas.FamApplicationCreate(**NEW_APPLICATION)
    app_data = crud_application.create_application(
        fam_application=app_data_as_pydantic, db=dbPgSession
    )

    # the object returned by create_application should contain the
    # application object that it was passed
    assert app_data.application_name == NEW_APPLICATION["application_name"]

    # verify that the data is in the database
    app_by_name = crud_application.get_application_by_name(
        db=dbPgSession, application_name=NEW_APPLICATION["application_name"]
    )
    assert app_by_name.application_name == NEW_APPLICATION["application_name"]


def test_delete_application(dbPgSession: Session):
    app_by_name = crud_application.get_application_by_name(
        db=dbPgSession, application_name=NEW_APPLICATION["application_name"]
    )
    assert app_by_name.application_name == NEW_APPLICATION["application_name"]

    crud_application.delete_application(
        db=dbPgSession,
        application_id=app_by_name.application_id
    )

    app_by_name = crud_application.get_application_by_name(
        db=dbPgSession, application_name=NEW_APPLICATION["application_name"]
    )
    assert app_by_name is None
