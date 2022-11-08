import datetime
import logging
import pytest

import api.app.models.model as model
import api.app.schemas as schemas
from api.app.crud import crud_application as crud_application
from api.app.crud import crud_role as crud_role


import fixtures.fixtures_crud_role as fixtures_crud_role

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def dbSession_famApplication_withdata(dbSession, applicationData1):
    applicationData1AsPydantic = schemas.FamApplicationCreate(
        **applicationData1)
    appData = crud_application.createFamApplication(
        famApplication=applicationData1AsPydantic,
        db=dbSession)

    yield dbSession

    dbSession.delete(appData)
    dbSession.commit()


@pytest.fixture(scope="function")
def applicationData1() -> dict:
    famAppData = {
        "application_name": 'test app',
        "application_description": "a really good app",
        'create_user': 'cognito client',
        'create_date': datetime.datetime.now(),
        'update_user': 'Ron Duguey',
        'update_date': datetime.datetime.now()
    }
    yield famAppData
    

@pytest.fixture(scope="function")
def dbSession_famApplication_withRoledata(
        dbSession_famApplication_withdata,
        dbSession_famRoletype,
        applicationData1,
        simpleRoleData,
        simpleRoleData2):
    
    # dbSession_famRoletype

    db = dbSession_famApplication_withdata
    # get the application id 
    app = crud_application.getApplicationByName(db=db,
       application_name=applicationData1['application_name'])
    app_id = app.application_id
    LOGGER.debug(f"app_id is: {app_id}")

    # create a couple of roles for the application
    simpleRoleData['application_id'] = app_id
    simpleRoleData2['application_id'] = app_id

    # add the roles to the database
    # famRole: schemas.FamRoleCreate, db: Session
    LOGGER.debug(f"simpleRoleData: {simpleRoleData}")
    simpleRoleDataPydantic = schemas.FamRoleCreate(**simpleRoleData)
    rl1 = crud_role.createFamRole(famRole=simpleRoleDataPydantic, db=db)
    LOGGER.debug(f"rl1: {rl1}")
    
    # simpleRoleDataPydantic2 = schemas.FamRoleCreate(**simpleRoleData2)
    # rl2 = crud_role.createFamRole(famRole=simpleRoleDataPydantic2, db=db)
    # LOGGER.debug(f"rl2: {rl2}")

    yield db

    db.delete(rl1)







    #dbSession.delete(appData)
    #dbSession.commit()


@pytest.fixture(scope="function")
def applicationRoleData(applicationData1, concreteRoleTypeRecord) -> dict:
    LOGGER.debug(f"concreteRoleTypeRecord: {concreteRoleTypeRecord}")
    applicationData1['role'] = [concreteRoleTypeRecord]
    yield applicationData1


