import logging

import pytest
import json
from api.app.main import apiPrefix

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"


def test_get_fam_application_nodata(testClient_fixture):
    response = testClient_fixture.get(f"{endPoint}/")
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 204
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert data == []


def test_get_fam_application(testApplication_fixture, applicationData1):
    response = testApplication_fixture.get(f"{endPoint}/")
    LOGGER.debug(f"response: {response}")
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert len(data) == 1
    assert data[0]["application_name"] == applicationData1["application_name"]


def test_delete_fam_application(testApplication_fixture, applicationData1):
    # verfiy that a record is being returned, so we have something to
    # be deleted
    response = testApplication_fixture.get(f"{endPoint}/")
    LOGGER.debug(f"response: {response}")
    data = response.json()
    assert len(data) == 1

    LOGGER.debug(f"data: {data}")

    appId = data[0]["application_id"]
    deleteEndPoint = f"{endPoint}/{appId}"
    response = testApplication_fixture.delete(deleteEndPoint)
    LOGGER.debug(f"response: {response.status_code}")

    # now verify that there are no application records
    getResp = testApplication_fixture.get(f"{endPoint}/")
    getData = getResp.json()
    assert getResp.status_code == 204
    assert getData == []


def test_post_fam_application(testClient_fixture, applicationData1):
    LOGGER.debug(f"applicationData1: {applicationData1}")
    applicationData1["create_date"] = str(applicationData1["create_date"])
    applicationData1["update_date"] = str(applicationData1["update_date"])
    postResp = testClient_fixture.post(f"{endPoint}/", json=applicationData1)
    LOGGER.debug(f"resp status: {postResp.status_code}")
    assert postResp.status_code == 200

    # make sure that there is data in the application
    getResp = testClient_fixture.get(f"{endPoint}/")
    getData = getResp.json()
    recordAdded = False
    testRecord = None
    for record in getData:
        LOGGER.debug(f"data: record: {record}")
        LOGGER.debug(f"applicationData1: {applicationData1}")
        if applicationData1["application_name"] == record["application_name"]:
            recordAdded = True
            testRecord = record
    assert recordAdded

    # cleanup after test
    deleteEndPoint = f"{endPoint}/{testRecord['application_id']}"
    deleteResponse = testClient_fixture.delete(deleteEndPoint)
    assert deleteResponse.status_code == 200
