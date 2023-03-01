import logging
import starlette.testclient
from api.app.main import apiPrefix
import tests.tests.jwt_utils as jwt_utils

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"


def test_get_applications(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))

    LOGGER.debug(f"response: {response}")
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert len(data) == 1
    assert data[0]["application_name"] == "FAM"
