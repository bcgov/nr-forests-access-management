import logging

import starlette
from api.app.main import apiPrefix
from api.app.schemas import FamForestClient
from api.app.constants import FamForestClientStatusType
import tests.tests.jwt_utils as jwt_utils

LOGGER = logging.getLogger(__name__)
endPoint_search = f"{apiPrefix}/forest_clients/search"


def test_search_client_number_not_exists_noresult(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    invalid_param = "?client_number=99999999"
    test_endPoint = endPoint_search + invalid_param
    LOGGER.debug(f"test_endPoint: {test_endPoint}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(f"{test_endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 0  # Expect empty

"""
    Client "00000001" have ACT (Active) status.
"""
def test_search_client_number_exists_with_one_result(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    exist_forest_client_number = "00000001"
    test_endPoint = endPoint_search + f"?client_number={exist_forest_client_number}"
    LOGGER.debug(f"test_endPoint: {test_endPoint}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(f"{test_endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    LOGGER.debug(data)
    assert len(data) == 1  # Expect only 1
    fc: FamForestClient = None
    try:
        fc = FamForestClient(**data[0])
    except Exception:
        assert False  # Conversion fail
    assert fc.forest_client_number == exist_forest_client_number

"""
    Forest Client API has following status codes.
        ACT (Active) - client "00000001"
        DAC (Deactivated) - client "00000002"
        DEC (Deceased)
        REC (Receivership)
        SPN (Suspended)
    FAM maps "ACT" to Active status internally; all other status are being
    mapped to Inactive.
"""
def test_search_client_number_with_inactive_status(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    # assert fc.status.status_code == FamForestClientStatusType.ACTIVE
    # TODO
    pass
