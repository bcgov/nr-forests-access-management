import logging
import pytest

import api.app.crud as crud


LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def testApplication_fixture(testClient_fixture, dbSession_famApplication_withdata):
    # using the fixture below to populate the database with data
    LOGGER.debug("got here")
    db = dbSession_famApplication_withdata
    yield testClient_fixture

# @pytest.fixture(scope="function")
# def testApplicationData():
#     applicationData = {
#         'application_name': 'habs_winner',
#         'application_description': 'creating the magic necessary for cup 25'
#     }
#     #crud.createFamApplication
#     yield applicationData
