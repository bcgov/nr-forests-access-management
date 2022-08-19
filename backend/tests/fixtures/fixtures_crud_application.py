import datetime
import logging
import pytest

import api.app.models.model as model
import api.app.schemas as schemas
from api.app.crud import crud_famApplication as crud_famApplication

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def dbSession_famApplication_withdata(dbSession, applicationData1):
    applicationData1AsPydantic = schemas.FamApplicationCreate(**applicationData1)
    appData = crud_famApplication.createFamApplication(famApplication=applicationData1AsPydantic,
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
