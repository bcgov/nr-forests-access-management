import datetime
import logging
import starlette.testclient
from typing import Dict, Union, TypedDict
from api.app.main import apiPrefix

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"


class ClientAndAppID(TypedDict):
    client: starlette.testclient.TestClient
    app_id: int


def test_get_fam_application_nodata(
        testClient_fixture: starlette.testclient.TestClient):
    response = testClient_fixture.get(f"{endPoint}")
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 204
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert data == []


def test_get_fam_application(
        testApplication_fixture: starlette.testclient.TestClient,
        applicationData1: Dict[str, Union[str, datetime.datetime]]):
    response = testApplication_fixture.get(f"{endPoint}/")
    LOGGER.debug(f"response: {response}")
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert len(data) == 1
    assert data[0]["application_name"] == applicationData1["application_name"]


def test_delete_fam_application(
        testApplication_fixture: starlette.testclient.TestClient,
        applicationData1:  Dict[str, Union[str, datetime.datetime]]):
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


def test_post_fam_application(
        testClient_fixture: starlette.testclient.TestClient,
        applicationData1: Dict[str, Union[str, datetime.datetime]]):
    LOGGER.debug(f"applicationData1: {applicationData1}")
    applicationData1["create_date"] = str(applicationData1["create_date"])
    applicationData1["update_date"] = str(applicationData1["update_date"])
    postResp = testClient_fixture.post(f"{endPoint}", json=applicationData1)
    LOGGER.debug(f"resp status: {postResp.status_code}")
    assert postResp.status_code == 200

    # make sure that there is data in the application
    getResp = testClient_fixture.get(f"{endPoint}")
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


def test_get_fam_application_roles(
        application_roles: ClientAndAppID,
        applicationData1: Dict[str, Union[str, datetime.datetime]],
        concreteRoleData,
        concreteRoleData2
        ):
    client = application_roles["client"]
    app_id = application_roles["app_id"]
    # need to get the app id

    roleEndPoint = endPoint + f"/{app_id}/fam_roles"
    LOGGER.debug(f"roleEndPoint: {roleEndPoint}")
    resp = client.get(roleEndPoint)
    LOGGER.debug(f"resp status: {resp.status_code}")
    resp_data = resp.json()
    LOGGER.debug(f"resp data as JSON: {resp.text}")
    LOGGER.debug(f"resp data as dict: {resp_data}")

    roleData = {}
    for returnRole in resp_data:
        roleData[returnRole['role_name']] = returnRole
    # organize into a dict with key as role_name

    roleName = concreteRoleData['role_name']
    returnRole = roleData[roleName]
    assert returnRole['role_purpose'] == concreteRoleData['role_purpose']
    assert returnRole['role_purpose'] == concreteRoleData['role_purpose']
    assert returnRole['application_id'] == app_id

    roleName = concreteRoleData2['role_name']
    returnRole = roleData[roleName]
    assert returnRole['role_purpose'] == concreteRoleData2['role_purpose']
    assert returnRole['role_purpose'] == concreteRoleData2['role_purpose']
    assert returnRole['application_id'] == app_id


def test_get_fam_user_role_assignment(
        application_role_assignment,
        applicationData1,
        concreteRoleData,
        concreteRoleData2,
        abstractRoleData,
        testUserData):

    client = application_role_assignment['client']
    app_id = application_role_assignment['app_id']

    roleEndPoint = endPoint + f"/{app_id}/user_role_assignment"
    resp = client.get(roleEndPoint)
    role_assignments = resp.json()
    LOGGER.debug(f"resp data: {role_assignments}")
    LOGGER.debug(f"json str: {resp.text}")

    # assert that there are 2 returned objects
    assert len(role_assignments) == 2

    role_names = []
    # getting the role names
    for assignment in role_assignments:
        role_names.append(assignment['role']['role_name'])

    assert concreteRoleData['role_name'] in role_names
    assert concreteRoleData2['role_name'] in role_names
    assert abstractRoleData['role_name'] not in role_names

    # assert the user that is assigned to the two roles is the correct user
    user_properties_2_check = ['user_type_code', 'cognito_user_id', 'user_name']
    for assignment in role_assignments:
        for property_to_check in user_properties_2_check:
            assert assignment['user'][property_to_check] == testUserData[property_to_check]






