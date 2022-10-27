import logging
import os

import api.app.models.model as models
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
    LOGGER.debug(f"returned from getFamApplications: {apps}")

    # if migrations have run then should already have 2, otherwise for blank db
    # should only be 1
    #assert len(apps) >= 1
    assert len(apps) > 99999999
    assert hasattr(apps[0], "application_name")
    # get all the apps into a list
    appNameList = []
    for app in apps:
        appNameList.append(app.application_name)

    # assert apps[0].application_name == applicationData1["application_name"]
    assert  applicationData1["application_name"] in appNameList

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
        appById = crud_application.getFamApplication(db=db, application_id=app.application_id)
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
    appData = crud_application.createFamApplication(famApplication=appDataAsPydantic, db=dbSession)
    #LOGGER.debug(f"appData: {}")

    # verify that the data is in the database
    famAppsAfter = crud_application.getFamApplications(dbSession)
    exists = False
    for famAppAfter in famAppsAfter:
        if famAppAfter.application_name == applicationData1["application_name"]:
            exists = True
            break

    assert exists
