import logging

import pytest
from api.app.main import apiPrefix

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"

def test_get_fam_application_nodata(testClient_fixture):
    response = testClient_fixture.get(endPoint)
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 204
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert data == []

def test_get_fam_application(testApplication_fixture, applicationData1):
    response = testApplication_fixture.get(endPoint)
    LOGGER.debug(f"response: {response}")
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert len(data) == 1
    assert data[0]['application_name'] == applicationData1['application_name']

def test_delete_fam_application(testApplication_fixture, applicationData1):
    # verfiy that a record is being returned, so we have something to
    # be deleted
    response = testApplication_fixture.get(endPoint)
    LOGGER.debug(f"response: {response}")
    data = response.json()
    assert len(data) == 1

    LOGGER.debug(f"data: {data}")

    appId = data[0]['application_id']
    deleteEndPoint = f"{endPoint}/{appId}"
    response = testApplication_fixture.delete(deleteEndPoint)
    LOGGER.debug(f"response: {response.status_code}")

    # now verify that we have data








