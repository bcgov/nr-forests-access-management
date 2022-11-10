import logging
import os
import sqlalchemy
from typing import Any, Dict

import api.app.schemas as schemas
from api.app.crud import crud_application as crud_application

LOGGER = logging.getLogger(__name__)


def test_getFamApplications(dbSession_famApplication_withdata, applicationData1):
    db = dbSession_famApplication_withdata

    LOGGER.debug(f"applicationData1: {applicationData1}")
    application1 = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    LOGGER.debug(f"application1: {application1}")
    apps = crud_application.getFamApplications(db=db)

    assert len(apps) == 1
    assert hasattr(apps[0], "application_name")
    assert apps[0].application_name == applicationData1["application_name"]


def test_getFamApplicationRoles(
    dbSession_famApplication_withRoledata: sqlalchemy.orm.session.Session,
    applicationData1: Dict[str, Any],
    applicationRoleData: Dict[str, Any],
    simpleRoleData,
    simpleRoleData2,
):
    """
    Tests the crud logic that sits behind the get application/roles
    dbSession_famApplication_withRoledata - database session with an test
        application record already loaded to the database, and two roles
    applicationData1 - A Dictionary describing the application record that is
        to be added to the database
    applicationRoleData - A Dictionary that
    """
    # get the application_id from the database for the record that was already
    # added in the fixture dbSession_famApplication_withRoledata
    db = dbSession_famApplication_withRoledata
    # getApplicationByName(db=db, application_name=)
    app = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    LOGGER.debug(f"applicationData1: {applicationData1}")
    appRoles = crud_application.getFamApplicationRoles(
        db=db, application_id=app.application_id
    )
    # double check that the app record was populated
    assert app.application_name == applicationData1["application_name"]
    LOGGER.debug(f"application1: {appRoles}")

    # need to convert this db query to a pydantic to see how
    # to handle the relationship, and if it gets properly serialized
    asSchema = schemas.FamApplicationRoleGet.from_orm(appRoles)
    asDict = asSchema.dict()
    LOGGER.debug(f"asDict: {asDict}")

    # assert that the roles we are expecting are present
    assert len(asDict["fam_role"]) == 2

    # get the role names from the returned record
    role_name_list = [role["role_name"] for role in asDict["fam_role"]]
    assert simpleRoleData["role_name"] in role_name_list
    assert simpleRoleData2["role_name"] in role_name_list


def test_deleteFamApplications(dbSession_famApplication_withdata, applicationData1):
    db = dbSession_famApplication_withdata
    # get list of applications from the database
    apps = crud_application.getFamApplications(db=db)
    # iterate over all of them and delete them
    for app in apps:
        crud_application.deleteFamApplication(db=db, application_id=app.application_id)

    # finally assert that there are no apps left in the database
    appsAfter = crud_application.getFamApplications(db=db)
    assert len(appsAfter) == 0


def test_getFamApplication(dbSession_famApplication_withdata, applicationData1):
    db = dbSession_famApplication_withdata
    apps = crud_application.getFamApplications(db=db)
    for app in apps:
        appById = crud_application.getFamApplication(
            db=db, application_id=app.application_id
        )
        assert appById.application_id == app.application_id


def test_getFamApplicationByName(dbSession_famApplication_withdata, applicationData1):
    db = dbSession_famApplication_withdata
    app = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    assert app.application_name == applicationData1["application_name"]


def test_getFamApplications_nodata(dbSession):
    """Was a starting place to figure out crud tests that work with the database
    session, not complete.  Assumes the database starts without any data.

    :param dbSession: sql alchemy database session
    :type dbSession: sqlalchemy.orm.Session
    """
    # TODO: start coding tests for crud.py code.
    files = os.listdir(".")
    LOGGER.debug(f"files: {files}")

    famApps = crud_application.getFamApplications(dbSession)
    assert famApps == []
    LOGGER.debug(f"famApps: {famApps}")


def test_createFamApplication(dbSession, applicationData1):
    # make sure we are starting off with no records
    famApps = crud_application.getFamApplications(dbSession)
    assert famApps == []

    # add the data to the database
    appDataAsPydantic = schemas.FamApplicationCreate(**applicationData1)
    appData = crud_application.createFamApplication(
        famApplication=appDataAsPydantic, db=dbSession
    )
    # the object returned by createFamApplication should contain the
    # application object that it was passed
    assert appData.application_name == applicationData1['application_name']
    # LOGGER.debug(f"appData: {}")

    # verify that the data is in the database
    famAppsAfter = crud_application.getFamApplications(dbSession)
    exists = False
    for famAppAfter in famAppsAfter:
        if famAppAfter.application_name == applicationData1["application_name"]:
            exists = True
            break

    assert exists
