import logging

import pytest
import tests.router.test_router_user as test_router_user

LOGGER = logging.getLogger(__name__)
endPoint = test_router_user.endPoint


@pytest.fixture(scope="function")
def user_client_withUsersNoCleanup(
    testClient_fixture, userData_Dict, dbSession_famUserTypes
):
    # used for delete, assumption is the test user that was created
    # has been cleaned up.
    userData_Dict["create_date"] = str(userData_Dict["create_date"])
    userData_Dict["update_date"] = str(userData_Dict["update_date"])

    resp = testClient_fixture.post(f"{endPoint}", json=userData_Dict)
    LOGGER.debug(f"setup user table with data: {resp.status_code} " + f"{resp.reason}")
    LOGGER.debug(f"setup user table with data: {resp.status_code} " + f"{resp.reason}")
    LOGGER.debug(f"setup data: {userData_Dict}")
    if resp.status_code != 200:
        raise ValueError(
            "should work! but... can't create this record: " +
            f" {userData_Dict}, the response is: {resp.reason}"
        )
    return testClient_fixture


@pytest.fixture(scope="function")
def user_client_withUsers(testClient_fixture, userData_Dict, dbSession_famUserTypes):
    userData_Dict["create_date"] = str(userData_Dict["create_date"])
    userData_Dict["update_date"] = str(userData_Dict["update_date"])

    resp = testClient_fixture.post(f"{endPoint}", json=userData_Dict)
    LOGGER.debug(f"setup user table with data: {resp.status_code}" + f"  {resp.reason}")
    if resp.status_code != 200:
        raise ValueError(
            "should work! but... can't create this record: " +
            f" {userData_Dict}, the response is: {resp.reason}"
        )
    yield testClient_fixture

    respData = resp.json()

    LOGGER.debug(f"delete result: {respData}")
    resp = testClient_fixture.delete(f"{endPoint}/{respData['user_id']}")
    LOGGER.debug(
        "status code from removing user_id: " +
        f"{respData['user_id']} {resp.status_code}"
    )
