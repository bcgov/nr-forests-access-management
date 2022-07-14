from starlette.testclient import TestClient

import os
import sys
import pytest
import logging

LOGGER = logging.getLogger(__name__)

# apiPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# print(apiPath)
# sys.path.insert(0, apiPath)

from api.app.main import app

# client = TestClient(app)


def test_get_fam_users_nodata(testClient_fixture):
    LOGGER.debug("here here here")
    response = testClient_fixture.get("/api/v1/fam_users")
    LOGGER.debug(f"response: {response}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 404
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert data == {"detail": "Not Found"}
    testClient_fixture.post()


def test_get_fam_users_withdata(user_client_withUsers):
    response = user_client_withUsers.get("/api/v1/fam_users")
    LOGGER.debug(f"response: {response}")
    data = response.json()
    LOGGER.debug(f"data: {data}")

def test_post_fam_users(testClient_fixture):
    user1 = {
        "user_type": "va",
        "cognito_user_id": "xyz123",
        "user_name": "Bill",
        "user_guid": "zzzuptop",
        "create_user": "Bill",
        "create_date": "2022-07-13T21:24:15.385Z",
        "update_user": "Bill",
        "update_date": "2022-07-13T21:24:15.385Z",
    }
    resp = testClient_fixture.post("/api/v1/fam_users", json=user1)
    body = resp.json()
    assert resp.status_code == 422
    user1['user_type'] = 'z'
    resp = testClient_fixture.post("/api/v1/fam_users", json=user1)
    assert resp.status_code == 200
    resp = testClient_fixture.delete("/api/v1/fam_users")


# follow this article.. best article I've found on testing
# https://www.jetbrains.com/pycharm/guide/tutorials/fastapi-aws-kubernetes/testing/


@pytest.fixture(scope="function")
def user_client_withUsers(testClient_fixture):
    user1 = {
        "user_type": "va",
        "cognito_user_id": "xyz123",
        "user_name": "Bill",
        "user_guid": "zzzuptop",
        "create_user": "Bill",
        "create_date": "2022-07-13T21:24:15.385Z",
        "update_user": "Bill",
        "update_date": "2022-07-13T21:24:15.385Z",
    }
    resp = testClient_fixture.post("/api/v1/fam_users", data=user1)
    LOGGER.debug(f"resp: {resp.status_code}  {resp.reason}")
    yield testClient_fixture
