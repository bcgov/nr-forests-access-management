import logging

import api.app.constants as constants
import pytest
import starlette
import testspg.jwt_utils as jwt_utils
from api.app.constants import FamForestClientStatusType
from api.app.main import apiPrefix
from api.app.schemas import FamForestClientSchema
from fastapi.testclient import TestClient
from testspg.constants import (FC_NUMBER_EXISTS_ACTIVE_00000001,
                               FC_NUMBER_EXISTS_DEACTIVATED,
                               FC_NUMBER_EXISTS_DECEASED,
                               FC_NUMBER_EXISTS_RECEIVERSHIP,
                               FC_NUMBER_EXISTS_SUSPENDED,
                               FOM_DEV_APPLICATION_ID)

LOGGER = logging.getLogger(__name__)
dummy_test_application_id_search_param = FOM_DEV_APPLICATION_ID
endPoint_search = f"{apiPrefix}/forest-clients/search?application_id={dummy_test_application_id_search_param}"


@pytest.mark.parametrize(
    "client_id_to_test, expcted_error_type",
    [("11", "string_too_short"), ("000001011", "string_too_long")],
)
def test_search_client_number_invalid_length_error(
    client_id_to_test,
    expcted_error_type,
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
):
    invalid_length_param = f"&client_number={client_id_to_test}"  # less than 8 digits
    test_end_point = endPoint_search + invalid_length_param
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert expcted_error_type in data["detail"][0]["type"]


def test_search_client_number_correct_length_not_valid_format(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    invalid_param = "&client_number=001a2b3d"
    test_end_point = endPoint_search + invalid_param
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    data = response.json()
    assert len(data) == 0  # Expect empty


def test_search_client_number_not_exists_noresult(
    test_client_fixture: TestClient, test_rsa_key
):
    invalid_param = "&client_number=99999999"
    test_end_point = endPoint_search + invalid_param
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    data = response.json()
    assert len(data) == 0  # Expect empty


def test_search_client_number_exists_with_one_result(
    test_client_fixture: TestClient, test_rsa_key
):
    """
    Client "00000001" have ACT (Active) status.
    """
    exist_forest_client_number = FC_NUMBER_EXISTS_ACTIVE_00000001
    test_end_point = endPoint_search + f"&client_number={exist_forest_client_number}"
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    data = response.json()
    assert len(data) == 1  # Expect only 1
    fc: FamForestClientSchema
    try:
        fc = FamForestClientSchema(**data[0])
    except Exception:
        assert (
            False  # If response data conversion fails, something is wrong in structure.
        )

    assert hasattr(fc, "client_name")
    assert hasattr(fc, "forest_client_number")
    assert hasattr(fc, "status")
    assert fc.forest_client_number == exist_forest_client_number


@pytest.mark.parametrize(
    "client_id_to_test, expcted_status",
    [
        (
            FC_NUMBER_EXISTS_ACTIVE_00000001,
            {
                "code": FamForestClientStatusType.ACTIVE,
                "description": constants.DESCRIPTION_ACTIVE,
            },
        ),
        (
            FC_NUMBER_EXISTS_DEACTIVATED,
            {
                "code": FamForestClientStatusType.INACTIVE,
                "description": constants.DESCRIPTION_INACTIVE,
            },
        ),
        (
            FC_NUMBER_EXISTS_DECEASED,
            {
                "code": FamForestClientStatusType.INACTIVE,
                "description": constants.DESCRIPTION_INACTIVE,
            },
        ),
        (
            FC_NUMBER_EXISTS_RECEIVERSHIP,
            {
                "code": FamForestClientStatusType.INACTIVE,
                "description": constants.DESCRIPTION_INACTIVE,
            },
        ),
        (
            FC_NUMBER_EXISTS_SUSPENDED,
            {
                "code": FamForestClientStatusType.INACTIVE,
                "description": constants.DESCRIPTION_INACTIVE,
            },
        ),
    ],
)
def test_search_client_number_with_status_mapping_correctly(
    client_id_to_test, expcted_status, test_client_fixture: TestClient, test_rsa_key
):
    """
    Forest Client API has following status codes.
        ACT (Active) - client "00000001"
        DAC (Deactivated) - client "00000002"
        DEC (Deceased) - client "00152880"
        REC (Receivership) - client "00169575"
        SPN (Suspended) - client "00003643"
    FAM maps "ACT" to Active status internally; all other status are being
    mapped to Inactive.
    """
    test_end_point = endPoint_search + f"&client_number={client_id_to_test}"
    LOGGER.debug(f"test_end_point: {test_end_point}")
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    data = response.json()
    assert len(data) == 1  # Expect only 1
    fc: FamForestClientSchema
    try:
        fc = FamForestClientSchema(**data[0])
    except Exception:
        assert False  # Conversion fail
    assert fc.forest_client_number == client_id_to_test
    assert fc.status.status_code == expcted_status["code"]
    assert fc.status.description == expcted_status["description"]
