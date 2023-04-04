
import logging

import pytest
from api.app import constants
from api.app.crud.crud_user_role import UserRoleValidator
from api.app.schemas import FamUserRoleAssignmentCreate
from mock import patch
from pydantic import ValidationError

LOGGER = logging.getLogger(__name__)

client_number_len_too_short = "0001011"
client_number_len_too_long = "000001011"
client_number_not_exists = "99999999"
"""
Forest Client API has following status codes.
    ACT (Active) - client "00000001"
    DAC (Deactivated) - client "00000002"
    DEC (Deceased) - client "00152880"
    REC (Receivership) - client "00169575"
    SPN (Suspended) - client "00003643"
"""
client_number_exists_active = "00000001"
client_number_exists_Deactivated = "00000002"
client_number_exists_Deceased = "00152880"
client_number_exists_Receivership = "00169575"
client_number_exists_Suspended = "00003643"

# Override this.
sample_request_dict = {
    "user_name": "test_user",
    "user_type_code": constants.UserType.IDIR,
    "role_id": 99,
    "forest_client_number": client_number_not_exists
}

# Override this.
sample_forest_client_return = [{
    'clientNumber': sample_request_dict["forest_client_number"],
    'clientName': 'Testing Org',
    'clientStatusCode': "some_api_client_status_code",
    'clientTypeCode': 'I', 'acronyms': []
}]


@pytest.fixture(scope="function", autouse=True)
def mock_forest_client():
    # Mocked dependency class object
    with patch("api.app.crud.crud_user_role.ForestClient", autospec=True) as m:
        yield m.return_value  # Very important to get instance of mocked class.


def test_init_with_request_param_client_number_too_long_error(
):
    request_dict = {**sample_request_dict, "forest_client_number": client_number_len_too_long}
    with pytest.raises(ValidationError, match="ensure this value has at most 8 characters"):
        request = FamUserRoleAssignmentCreate(**request_dict)
        UserRoleValidator(request)


@pytest.mark.parametrize("client_id_to_test, expcted_result", [
    (client_number_len_too_short, {"api_client_status_code": None, "exists": False}),
    (client_number_not_exists, {"api_client_status_code": None, "exists": False}),
    (client_number_exists_active, {"api_client_status_code": "ACT", "exists": True}),
    (client_number_exists_Deactivated, {"api_client_status_code": "DAC", "exists": True}),
    (client_number_exists_Deceased, {"api_client_status_code": "DEC", "exists": True}),
    (client_number_exists_Receivership, {"api_client_status_code": "REC", "exists": True}),
    (client_number_exists_Suspended, {"api_client_status_code": "SPN", "exists": True}),
])
def test_forest_client_number_exists(
    client_id_to_test,
    expcted_result,
    mock_forest_client,
):
    request_dict = {**sample_request_dict, "forest_client_number": client_id_to_test}
    mock_forest_client.find_by_client_number.return_value = __to_mock_forest_client_return(
        request_dict["forest_client_number"],
        expcted_result["api_client_status_code"]
    )

    request = FamUserRoleAssignmentCreate(**request_dict)
    validator = UserRoleValidator(request)
    result = validator.forest_client_number_exists()

    mock_forest_client.find_by_client_number.assert_called_with(client_id_to_test)
    assert result is expcted_result["exists"]


@pytest.mark.parametrize("client_id_to_test, expcted_result", [
    (client_number_len_too_short, {"api_client_status_code": None}),
    (client_number_not_exists, {"api_client_status_code": None}),
    (client_number_exists_active, {"api_client_status_code": "ACT"}),
    (client_number_exists_Deactivated, {"api_client_status_code": "DAC"}),
    (client_number_exists_Deceased, {"api_client_status_code": "DEC"}),
    (client_number_exists_Receivership, {"api_client_status_code": "REC"}),
    (client_number_exists_Suspended, {"api_client_status_code": "SPN"}),
])
def test_get_forst_client(
    client_id_to_test,
    expcted_result,
    mock_forest_client,
):
    request_dict = {**sample_request_dict, "forest_client_number": client_id_to_test}
    mock_forest_client.find_by_client_number.return_value = __to_mock_forest_client_return(
        request_dict["forest_client_number"],
        expcted_result["api_client_status_code"]
    )

    request = FamUserRoleAssignmentCreate(**request_dict)
    validator = UserRoleValidator(request)
    result = validator.get_forest_client()

    mock_forest_client.find_by_client_number.assert_called_with(client_id_to_test)
    assert (result is mock_forest_client.find_by_client_number.return_value[0]
            if expcted_result["api_client_status_code"] is not None
            else result is None)


@pytest.mark.parametrize("client_id_to_test, expcted_result", [
    (client_number_len_too_short, {"api_client_status_code": None, "is_active": False}),
    (client_number_not_exists, {"api_client_status_code": None, "is_active": False}),
    (client_number_exists_active, {"api_client_status_code": "ACT", "is_active": True}),
    (client_number_exists_Deactivated, {"api_client_status_code": "DAC", "is_active": False}),
    (client_number_exists_Deceased, {"api_client_status_code": "DEC", "is_active": False}),
    (client_number_exists_Receivership, {"api_client_status_code": "REC", "is_active": False}),
    (client_number_exists_Suspended, {"api_client_status_code": "SPN", "is_active": False}),
])
def test_forest_client_active(
    client_id_to_test,
    expcted_result,
    mock_forest_client,
):
    request_dict = {**sample_request_dict, "forest_client_number": client_id_to_test}
    mock_forest_client.find_by_client_number.return_value = __to_mock_forest_client_return(
        request_dict["forest_client_number"],
        expcted_result["api_client_status_code"]
    )

    request = FamUserRoleAssignmentCreate(**request_dict)
    validator = UserRoleValidator(request)
    result = validator.forest_client_active()

    mock_forest_client.find_by_client_number.assert_called_with(client_id_to_test)
    assert result is expcted_result["is_active"]


def __to_mock_forest_client_return(forest_client_number, api_client_status_code):
    return (
        [{
            **sample_forest_client_return[0],
            'clientNumber': forest_client_number,
            'clientStatusCode': api_client_status_code
        }]
        if api_client_status_code is not None
        else []
    )