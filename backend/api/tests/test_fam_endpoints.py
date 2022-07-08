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

client = TestClient(app)


def test_get_fam_users(test_fixture):
    LOGGER.debug("here here here")
    response = client.get("/fam_users")
    LOGGER.debug(f"response: {response}")
    LOGGER.debug(f"response {test_fixture}")
    #assert response.status_code == 200
    #assert response.json() == {"ping": "pong!"}

# follow this article.. best article I've found on testing
# https://www.jetbrains.com/pycharm/guide/tutorials/fastapi-aws-kubernetes/testing/