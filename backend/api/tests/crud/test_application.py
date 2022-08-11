import logging
import os

import api.app.crud as crud
import api.app.models.model as models


LOGGER = logging.getLogger(__name__)


def test_getFamApplications_withData(dbSession_famApplication_withdata, applicationData1):
    db = dbSession_famApplication_withdata

    LOGGER.debug(f"applicationData1: {applicationData1}")
    application1 = crud.getApplicationByName(db=db, application_name=applicationData1['application_name'])
    LOGGER.debug(f"application1: {application1}")
    apps = crud.getFamApplications(db=db)
    assert len(apps) > 0

    #application = crud.deleteApplication(db=db, application_id=application1.application_id)
    #LOGGER.debug(f"application : {application}")
    #assert application['application_name'] == applicationData1['application_name']


def test_getFamApplications_nodata(dbSession):
    """Was a starting place to figure out crud tests that work with the database
    session, not complete.  Assumes the database starts without any data.

    :param dbSession: sql alchemy database session
    :type dbSession: sqlalchemy.orm.Session
    """
    # TODO: start coding tests for crud.py code.
    files = os.listdir(".")
    LOGGER.debug(f"files: {files}")

    famApps = crud.getFamApplications(dbSession)
    assert famApps == []
    LOGGER.debug(f"famApps: {famApps}")

