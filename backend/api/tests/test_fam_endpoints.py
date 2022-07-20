import logging

import pytest
from api.app.main import apiPrefix

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_users"


def test_get_fam_users_nodata(testClient_fixture):
    LOGGER.debug("here here here")
    response = testClient_fixture.get(endPoint)
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 200
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert data == []


def test_get_fam_users_withdata(user_client_withUsers):
    response = user_client_withUsers.get(endPoint)
    LOGGER.debug(f"response: {response}")
    data = response.json()
    LOGGER.debug(f"data: {data}")


def test_delete_fam_user(user_client_withUsersNoCleanup, testClient_fixture):
    response = user_client_withUsersNoCleanup.get(endPoint)
    LOGGER.debug(f"response: {response}")
    respData = response.json()
    LOGGER.debug(f"data: {respData}")
    # start of by making sure we have data
    assert len(respData) > 0 and "user_type" in respData[0]

    # delete the data
    respDelete = user_client_withUsersNoCleanup.delete(
        f"{endPoint}/{respData[0]['user_id']}"
    )
    LOGGER.debug(f"delete resp: {respDelete.reason}")
    assert respDelete.status_code == 200

    # double check that the record is missing from the data now
    # testClient_fixture.
    responseAD = testClient_fixture.get(endPoint)
    respDataADData = responseAD.json()
    for i in respDataADData:
        if i["user_id"] == respData[0]["user_id"]:
            LOGGER.debug("response data... record didnt get deleted: " +
                         f"{respData[0]}")
        assert i["user_id"] != respData[0]["user_id"]


def test_get_fam_user(user_client_withUsers):
    # retrieval of user is by id, don't know what id got
    # assigned so getting all the users, from that can
    # test the get individual user end point
    allUsersResponse = user_client_withUsers.get(endPoint)
    allUsersData = allUsersResponse.json()
    LOGGER.debug(f"user data: {allUsersData}")
    for user in allUsersData:
        singleUser = user_client_withUsers.get(f"{endPoint}/{user['user_id']}")
        singleUserData = singleUser.json()
        assert singleUserData == user


def test_post_fam_users(testClient_fixture, testUserData):

    # modify the user data to make it invalid
    testUserData["user_type"] = "invalid data"
    testUserData['create_date'] = str(testUserData['create_date'])
    testUserData['update_date'] = str(testUserData['update_date'])

    resp = testClient_fixture.post(endPoint, json=testUserData)
    body = resp.json()
    LOGGER.debug(f"body: {body}")
    assert resp.status_code == 422
    expectedMessage = 'value for user_type provided was invalid data, ' + \
        "user_type length cannot exceed 1 character"
    assert body['detail'][0]['msg'] == expectedMessage

    # fix the data so the post should succeed
    testUserData["user_type"] = "z"
    resp = testClient_fixture.post(endPoint, json=testUserData)
    respData = resp.json()
    LOGGER.debug(f"resp data: {resp.json()}")
    assert resp.status_code == 200

    # verify that a record with the same guid cannot be entered
    respDataCopy = respData.copy()
    del respDataCopy["user_id"]
    resp = testClient_fixture.post(endPoint, json=respDataCopy)
    respBody = resp.json()
    LOGGER.debug(f"resp data: {resp.status_code} - {resp.json()}")
    assert resp.status_code == 422
    assert "IntegrityError" in respBody["detail"]

    # cleanup by deleting the user
    resp = testClient_fixture.delete(f"{endPoint}/{respData['user_id']}")
    data = resp.json()
    LOGGER.debug(f"result: {data} {resp.status_code}")
    # making sure the delete was successful, but not testing delete end point
    # here
    assert resp.status_code == 200


# follow this article.. best article I've found on testing
# https://www.jetbrains.com/pycharm/guide/tutorials/fastapi-aws-kubernetes/testing/


@pytest.fixture(scope="function")
def user_client_withUsersNoCleanup(testClient_fixture, testUserData):
    # used for delete, assumption is the test user that was created
    # has been cleaned up.
    testUserData['create_date'] = str(testUserData['create_date'])
    testUserData['update_date'] = str(testUserData['update_date'])

    resp = testClient_fixture.post(endPoint, json=testUserData)
    LOGGER.debug(f"setup user table with data: {resp.status_code} " +
                 f"{resp.reason}")
    LOGGER.debug(f"setup data: {testUserData}")
    if resp.status_code != 200:
        raise ValueError(
            "should work! but... can't create this record: "
            + f" {testUserData}, the response is: {resp.reason}"
        )
    return testClient_fixture


@pytest.fixture(scope="function")
def user_client_withUsers(testClient_fixture, testUserData):
    testUserData['create_date'] = str(testUserData['create_date'])
    testUserData['update_date'] = str(testUserData['update_date'])

    resp = testClient_fixture.post(endPoint, json=testUserData)
    LOGGER.debug(f"setup user table with data: {resp.status_code}" +
                 f"  {resp.reason}")
    if resp.status_code != 200:
        raise ValueError(
            "should work! but... can't create this record: "
            + f" {testUserData}, the response is: {resp.reason}"
        )
    yield testClient_fixture

    respData = resp.json()

    LOGGER.debug(f"delete result: {respData}")
    resp = testClient_fixture.delete(f"{endPoint}/{respData['user_id']}")
    LOGGER.debug(
        "status code from removing user_id: " +
        f"{respData['user_id']} {resp.status_code}"
    )
