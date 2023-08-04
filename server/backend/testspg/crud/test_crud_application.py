from sqlalchemy.orm import Session
import logging
import datetime
import pytest
from sqlalchemy.exc import NoResultFound
from api.app.crud import crud_application
import api.app.schemas as schemas
import api.app.constants as constants
from testspg.constants import (
    TEST_NOT_EXIST_APPLICATION_ID,
    TEST_FOM_DEV_APPLICATION_ID,
    TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    TEST_NOT_EXIST_ROLE_ID,
)

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


def test_get_applications(db_pg_connection: Session):
    apps = crud_application.get_applications(db=db_pg_connection)
    assert len(apps) > 1
    assert apps[0].application_name == TEST_APPLICATION_NAME_FAM
    assert apps[1].application_name == TEST_APPLICATION_NAME_FOM_DEV
    assert apps[1].app_environment == "DEV"


def test_get_application(db_pg_connection: Session):
    apps = crud_application.get_applications(db=db_pg_connection)
    assert len(apps) > 1

    for app in apps:
        app_by_id = crud_application.get_application(
            db=db_pg_connection, application_id=app.application_id
        )
        assert app_by_id.application_id == app.application_id

    app_by_id = crud_application.get_application(
        db=db_pg_connection, application_id=TEST_APPLICATION_ID_FAM
    )
    assert app_by_id.application_id == TEST_APPLICATION_ID_FAM
    assert app_by_id.application_name == TEST_APPLICATION_NAME_FAM

    app_by_id = crud_application.get_application(
        db=db_pg_connection, application_id=TEST_NOT_EXIST_APPLICATION_ID
    )
    assert app_by_id is None


def test_get_application_by_name(db_pg_connection: Session):
    apps = crud_application.get_applications(db=db_pg_connection)
    assert len(apps) > 1

    for app in apps:
        app_by_name = crud_application.get_application_by_name(
            db=db_pg_connection, application_name=app.application_name
        )
        assert app_by_name.application_name == app.application_name

    app_by_name = crud_application.get_application_by_name(
        db=db_pg_connection, application_name=TEST_APPLICATION_NAME_FAM
    )
    assert app_by_name.application_id == TEST_APPLICATION_ID_FAM
    assert app_by_name.application_name == TEST_APPLICATION_NAME_FAM

    app_by_name = crud_application.get_application_by_name(
        db=db_pg_connection, application_name=TEST_APPLICATION_NAME_NOT_FOUND
    )
    assert app_by_name is None


def test_get_application_roles(db_pg_connection: Session):
    app_roles = crud_application.get_application_roles(
        db=db_pg_connection, application_id=TEST_FOM_DEV_APPLICATION_ID
    )

    for app_role in app_roles:
        # test the schema definitions work, will raise error if they do not
        schemas.FamApplicationRole.from_orm(app_role)

    assert len(app_roles) == 2

    fom_reviewer_role_found = False
    fom_submitter_role_found = False

    for app_role in app_roles:
        if (
            app_role.role_name == TEST_APPLICATION_ROLES_FOM_DEV[0]
            and app_role.application_id == TEST_FOM_DEV_APPLICATION_ID
            and app_role.role_type_code == "A"
        ):
            fom_submitter_role_found = True
        elif (
            app_role.role_name == TEST_APPLICATION_ROLES_FOM_DEV[1]
            and app_role.application_id == TEST_FOM_DEV_APPLICATION_ID
            and app_role.role_type_code == "C"
        ):
            fom_reviewer_role_found = True

    assert fom_submitter_role_found, f"Expected role {TEST_APPLICATION_ROLES_FOM_DEV[0]} in results"
    assert fom_reviewer_role_found, f"Expected role {TEST_APPLICATION_ROLES_FOM_DEV[1]} in results"


def test_get_application_id_by_role_id(db_pg_connection: Session):
    app_id = crud_application.get_application_id_by_role_id(
        db=db_pg_connection, role_id=TEST_FOM_DEV_SUBMITTER_ROLE_ID
    )
    assert app_id == TEST_FOM_DEV_APPLICATION_ID


def test_get_application_id_by_user_role_xref_id(db_pg_connection: Session):
    app_id = crud_application.get_application_id_by_user_role_xref_id(
        db=db_pg_connection,
        user_role_xref_id=1,  # the first user in our db has role FAM admin
    )
    assert app_id == TEST_APPLICATION_ROLE_ID_FAM


# def test_create_application(db_pg_connection: Session):
#     # get non existing application
#     app_by_name = crud_application.get_application_by_name(
#         db=db_pg_connection, application_name=NEW_APPLICATION["application_name"]
#     )
#     assert app_by_name is None

#     # add a new application to the database
#     app_data_as_pydantic = schemas.FamApplicationCreate(**NEW_APPLICATION)
#     new_app = crud_application.create_application(
#         fam_application=app_data_as_pydantic, db=db_pg_connection
#     )

#     # the object returned by create_application should contain the
#     # application object that it was passed
#     assert new_app.application_name == NEW_APPLICATION["application_name"]

#     # verify that the data is in the database
#     app_by_name = crud_application.get_application_by_name(
#         db=db_pg_connection, application_name=NEW_APPLICATION["application_name"]
#     )
#     assert app_by_name.application_name == NEW_APPLICATION["application_name"]

#     # cleanup
#     crud_application.delete_application(
#         db=db_pg_connection, application_id=app_by_name.application_id
#     )


# def test_delete_application(db_pg_connection: Session):
#     # delete non exists application
#     app_by_name = crud_application.get_application_by_name(
#         db=db_pg_connection, application_name=NEW_APPLICATION["application_name"]
#     )
#     assert app_by_name is None

#     with pytest.raises(NoResultFound) as e:
#         crud_application.delete_application(db_pg_connection, TEST_NOT_EXIST_ROLE_ID)
#     assert str(e.value) == "No row was found when one was required"

#     # create a new app
#     app_data_as_pydantic = schemas.FamApplicationCreate(**NEW_APPLICATION)
#     crud_application.create_application(
#         fam_application=app_data_as_pydantic, db=db_pg_connection
#     )
#     # verify the new application is in the database
#     app_by_name = crud_application.get_application_by_name(
#         db=db_pg_connection, application_name=NEW_APPLICATION["application_name"]
#     )
#     assert app_by_name.application_name == NEW_APPLICATION["application_name"]
#     # delete the application
#     crud_application.delete_application(
#         db=db_pg_connection, application_id=app_by_name.application_id
#     )
#     # verify application got deleted
#     app_by_name = crud_application.get_application_by_name(
#         db=db_pg_connection, application_name=NEW_APPLICATION["application_name"]
#     )
#     assert app_by_name is None
