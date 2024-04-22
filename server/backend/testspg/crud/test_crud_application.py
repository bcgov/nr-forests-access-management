import datetime
import logging

import api.app.constants as constants
import api.app.schemas as schemas
from api.app.crud import crud_application
from sqlalchemy.orm import Session
from testspg.constants import (FOM_DEV_APPLICATION_ID,
                               NOT_EXIST_APPLICATION_ID)

LOGGER = logging.getLogger(__name__)

TEST_APPLICATION_NAME_NOT_FOUND = "NOT_FOUND"

TEST_APPLICATION_NAME_FAM = "FAM"
TEST_APPLICATION_ID_FAM = 1
TEST_APPLICATION_ROLE_ID_FAM = 1

TEST_APPLICATION_NAME_FOM_DEV = "FOM_DEV"
TEST_APPLICATION_ROLES_FOM_DEV = ["FOM_SUBMITTER", "FOM_REVIEWER"]

NEW_APPLICATION = {
    "application_name": "TEST_APP_DEV",
    "application_description": "A testing application",
    "app_environment": constants.AppEnv.APP_ENV_TYPE_DEV,
    "create_user": constants.FAM_PROXY_API_USER,
    "create_date": datetime.datetime.now(),
    "update_user": "Tester",
    "update_date": datetime.datetime.now(),
}


def test_get_applications(db_pg_session: Session):
    apps = crud_application.get_applications(db=db_pg_session)
    assert len(apps) > 1
    assert apps[0].application_name == TEST_APPLICATION_NAME_FAM
    assert apps[1].application_name == TEST_APPLICATION_NAME_FOM_DEV
    assert apps[1].app_environment == "DEV"


def test_get_application(db_pg_session: Session):
    apps = crud_application.get_applications(db=db_pg_session)
    assert len(apps) > 1

    for app in apps:
        app_by_id = crud_application.get_application(
            db=db_pg_session, application_id=app.application_id
        )
        assert app_by_id.application_id == app.application_id

    app_by_id = crud_application.get_application(
        db=db_pg_session, application_id=TEST_APPLICATION_ID_FAM
    )
    assert app_by_id.application_id == TEST_APPLICATION_ID_FAM
    assert app_by_id.application_name == TEST_APPLICATION_NAME_FAM

    app_by_id = crud_application.get_application(
        db=db_pg_session, application_id=NOT_EXIST_APPLICATION_ID
    )
    assert app_by_id is None


def test_get_application_by_name(db_pg_session: Session):
    apps = crud_application.get_applications(db=db_pg_session)
    assert len(apps) > 1

    for app in apps:
        app_by_name = crud_application.get_application_by_name(
            db=db_pg_session, application_name=app.application_name
        )
        assert app_by_name.application_name == app.application_name

    app_by_name = crud_application.get_application_by_name(
        db=db_pg_session, application_name=TEST_APPLICATION_NAME_FAM
    )
    assert app_by_name.application_id == TEST_APPLICATION_ID_FAM
    assert app_by_name.application_name == TEST_APPLICATION_NAME_FAM

    app_by_name = crud_application.get_application_by_name(
        db=db_pg_session, application_name=TEST_APPLICATION_NAME_NOT_FOUND
    )
    assert app_by_name is None


def test_get_application_roles(db_pg_session: Session):
    app_roles = crud_application.get_application_roles(
        db=db_pg_session, application_id=FOM_DEV_APPLICATION_ID
    )

    for app_role in app_roles:
        # test the schema definitions work, will raise error if they do not
        schemas.FamApplicationRole.model_validate(app_role)

    assert len(app_roles) == 2

    fom_reviewer_role_found = False
    fom_submitter_role_found = False

    for app_role in app_roles:
        if (
            app_role.role_name == TEST_APPLICATION_ROLES_FOM_DEV[0]
            and app_role.application_id == FOM_DEV_APPLICATION_ID
            and app_role.role_type_code == "A"
        ):
            fom_submitter_role_found = True
        elif (
            app_role.role_name == TEST_APPLICATION_ROLES_FOM_DEV[1]
            and app_role.application_id == FOM_DEV_APPLICATION_ID
            and app_role.role_type_code == "C"
        ):
            fom_reviewer_role_found = True

    assert fom_submitter_role_found, f"Expected role {TEST_APPLICATION_ROLES_FOM_DEV[0]} in results"
    assert fom_reviewer_role_found, f"Expected role {TEST_APPLICATION_ROLES_FOM_DEV[1]} in results"



