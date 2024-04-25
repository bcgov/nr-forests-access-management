
import logging

import pytest
from api.app import constants
from api.app.crud.crud_user_role import UserRoleValidator
from api.app.schemas import FamUserRoleAssignmentCreate
from mock import patch
from pydantic import ValidationError
from testspg.constants import (FC_NUMBER_EXISTS_ACTIVE_00000001,
                               FC_NUMBER_EXISTS_DEACTIVATED,
                               FC_NUMBER_EXISTS_DECEASED,
                               FC_NUMBER_EXISTS_RECEIVERSHIP,
                               FC_NUMBER_EXISTS_SUSPENDED,
                               FC_NUMBER_LEN_TOO_LONG,
                               FC_NUMBER_LEN_TOO_SHORT,
                               FC_NUMBER_NOT_EXISTS)

LOGGER = logging.getLogger(__name__)

# Override this.
sample_request_dict = {
    "user_name": "test_user",
    "user_type_code": constants.UserType.IDIR,
    "role_id": 99,
    "forest_client_number": FC_NUMBER_NOT_EXISTS
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
    with patch("api.app.crud.crud_user_role.ForestClientService", autospec=True) as m:
        yield m.return_value  # Very important to get instance of mocked class.


def test_init_with_request_param_client_number_too_long_error(
):
    request_dict = {**sample_request_dict, "forest_client_number": FC_NUMBER_LEN_TOO_LONG}
    with pytest.raises(ValidationError, match="String should have at most 8 characters"):
        request = FamUserRoleAssignmentCreate(**request_dict)
        UserRoleValidator(request)


@pytest.mark.parametrize("client_id_to_test, expcted_result", [
    (FC_NUMBER_LEN_TOO_SHORT, {"api_client_status_code": None, "exists": False}),
    (FC_NUMBER_NOT_EXISTS, {"api_client_status_code": None, "exists": False}),
    (FC_NUMBER_EXISTS_ACTIVE_00000001, {"api_client_status_code": "ACT", "exists": True}),
    (FC_NUMBER_EXISTS_DEACTIVATED, {"api_client_status_code": "DAC", "exists": True}),
    (FC_NUMBER_EXISTS_DECEASED, {"api_client_status_code": "DEC", "exists": True}),
    (FC_NUMBER_EXISTS_RECEIVERSHIP, {"api_client_status_code": "REC", "exists": True}),
    (FC_NUMBER_EXISTS_SUSPENDED, {"api_client_status_code": "SPN", "exists": True}),
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
    (FC_NUMBER_LEN_TOO_SHORT, {"api_client_status_code": None}),
    (FC_NUMBER_NOT_EXISTS, {"api_client_status_code": None}),
    (FC_NUMBER_EXISTS_ACTIVE_00000001, {"api_client_status_code": "ACT"}),
    (FC_NUMBER_EXISTS_DEACTIVATED, {"api_client_status_code": "DAC"}),
    (FC_NUMBER_EXISTS_DECEASED, {"api_client_status_code": "DEC"}),
    (FC_NUMBER_EXISTS_RECEIVERSHIP, {"api_client_status_code": "REC"}),
    (FC_NUMBER_EXISTS_SUSPENDED, {"api_client_status_code": "SPN"}),
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
    (FC_NUMBER_LEN_TOO_SHORT, {"api_client_status_code": None, "is_active": False}),
    (FC_NUMBER_NOT_EXISTS, {"api_client_status_code": None, "is_active": False}),
    (FC_NUMBER_EXISTS_ACTIVE_00000001, {"api_client_status_code": "ACT", "is_active": True}),
    (FC_NUMBER_EXISTS_DEACTIVATED, {"api_client_status_code": "DAC", "is_active": False}),
    (FC_NUMBER_EXISTS_DECEASED, {"api_client_status_code": "DEC", "is_active": False}),
    (FC_NUMBER_EXISTS_RECEIVERSHIP, {"api_client_status_code": "REC", "is_active": False}),
    (FC_NUMBER_EXISTS_SUSPENDED, {"api_client_status_code": "SPN", "is_active": False}),
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