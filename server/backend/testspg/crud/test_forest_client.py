

import logging

import pytest

from server.backend.api.app.integration.forest_client.forest_client_integration import \
    ForestClientIntegrationService

LOGGER = logging.getLogger(__name__)


class TestForestClientServiceClass(object):
    """
    Testing ForestClientService class with real remote API calls (TEST environment).
    Initially Forest Client API returns also "acronyms" field but it disappears
    some day. Since this field is not important at the moment, so test does not
    includ3e it.
    """
    fc_api: ForestClientIntegrationService
    example_expected_valid_result = {
        'clientNumber': '00000002',
        'clientName': 'PENDING S & R BILLING',
        'clientStatusCode': 'DAC',
        'clientTypeCode': 'G'
    }

    def setup_class(self):
        self.fc_api = ForestClientIntegrationService()

    def test_verify_init(self):
        # Quick Verifying for init not empty
        assert self.fc_api.api_base_url is not None
        assert "/api/clients" in self.fc_api.api_clients_url
        assert self.fc_api.API_TOKEN is not None
        assert self.fc_api.headers["X-API-KEY"] == self.fc_api.API_TOKEN

    @pytest.mark.parametrize("client_id_to_test, expcted_result", [
        ("0001011", []),  # less than 8 digits.
        ("99999999", []),  # 8 digits - client not exist.
        ("000001011", [])  # more than 8 digits.
    ])
    def test_find_by_client_number_not_exists_noresult(self, client_id_to_test, expcted_result):
        assert self.fc_api.find_by_client_number(client_id_to_test) == expcted_result

    def test_find_by_client_number_exists_returns_list_one_item(self):
        """
        The test validating API does return single client dictionary and
        with the expected key(s) structure.
        """
        client_id_to_test = self.example_expected_valid_result["clientNumber"]
        result = self.fc_api.find_by_client_number(client_id_to_test)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        result_fc_dict = result[0]
        assert all(key in self.example_expected_valid_result.keys() for key in result_fc_dict.keys())
