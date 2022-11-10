import datetime
import logging
import pytest
import sqlalchemy
from typing import Any, Dict, Generator, Union

import api.app.schemas as schemas
from api.app.crud import crud_application as crud_application
from api.app.crud import crud_role as crud_role


LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def dbSession_famApplication_withdata(
    dbSession_famRoletype, applicationData1
) -> sqlalchemy.orm.session.Session:
    db = dbSession_famRoletype
    applicationData1AsPydantic = schemas.FamApplicationCreate(**applicationData1)
    appData = crud_application.createFamApplication(
        famApplication=applicationData1AsPydantic, db=db
    )

    try:
        db.delete(appData)
        db.commit()
    except sqlalchemy.orm.exc.ObjectDeletedError as e:
        LOGGER.debug(f"exception: {e}")
        LOGGER.debug(f"{type(e).__name__}")
        LOGGER.debug("app object was already deleted")

    try:
        db.delete(appData)
        db.commit()
    except sqlalchemy.orm.exc.ObjectDeletedError as e:
        LOGGER.debug("app object was already deleted")
        LOGGER.debug(f"{type(e).__name__}")
        db.rollback()
    except Exception as e:
        LOGGER.debug(f"exception: {e}")
        LOGGER.debug(f"{type(e).__name__}")
        raise


@pytest.fixture(scope="function")
def applicationData1() -> Generator[
    Dict[str, Union[str, datetime.datetime]], None, None
]:
    famAppData = {
        "application_name": "test app",
        "application_description": "a really good app",
        "create_user": "cognito client",
        "create_date": datetime.datetime.now(),
        "update_user": "Ron Duguey",
        "update_date": datetime.datetime.now(),
    }
    yield famAppData


@pytest.fixture(scope="function")
def dbSession_famApplication_withRoledata(
    dbSession_famApplication_withdata,
    applicationData1,
    simpleRoleData,
    simpleRoleData2,
):
    db = dbSession_famApplication_withdata
    db.flush()
    # get the application id
    app = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    app_id = app.application_id
    LOGGER.debug(f"app_id is: {app_id}")

    # create a couple of roles for the application
    simpleRoleData["application_id"] = app_id
    simpleRoleData2["application_id"] = app_id

    # add the roles to the database
    # famRole: schemas.FamRoleCreate, db: Session
    LOGGER.debug(f"simpleRoleData: {simpleRoleData}")
    simpleRoleDataPydantic = schemas.FamRoleCreate(**simpleRoleData)
    rl1 = crud_role.createFamRole(famRole=simpleRoleDataPydantic, db=db)
    LOGGER.debug(f"rl1: {rl1}")

    simpleRoleDataPydantic2 = schemas.FamRoleCreate(**simpleRoleData2)
    rl2 = crud_role.createFamRole(famRole=simpleRoleDataPydantic2, db=db)
    # LOGGER.debug(f"rl2: {rl2}")

    yield db

    db.delete(rl1)
    db.delete(rl2)
    db.commit()


@pytest.fixture(scope="function")
def applicationRoleData(applicationData1, concreteRoleTypeRecord) -> Dict[str, Any]:
    LOGGER.debug(f"concreteRoleTypeRecord: {concreteRoleTypeRecord}")
    applicationData1["role"] = [concreteRoleTypeRecord]
    yield applicationData1
