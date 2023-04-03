

import pytest
import logging
from api.app.integration.forest_client.forest_client import ForestClient

LOGGER = logging.getLogger(__name__)


class TestForestClientClass(object):
    fc_api: ForestClient = None

    def setup_class(self):
        self.fc_api = ForestClient()

    def test_verify_init(self):
        # Quick Verifying for init not empty
        assert self.fc_api.api_base_url is not None
        assert self.fc_api.api_clients_url is not None
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
        client_id_to_test = "00000002"
        result = self.fc_api.find_by_client_number(client_id_to_test)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        assert "clientName" in result[0]
        assert "clientNumber" in result[0]
        assert "clientStatusCode" in result[0]
