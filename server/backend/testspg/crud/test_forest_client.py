

import logging

import pytest
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.schemas.forest_client_integration import \
    ForestClientIntegrationSearchParmsSchema

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
    def test_search__client_number_not_exists_no_result(self, client_id_to_test, expcted_result):
        assert self.fc_api.search(
            ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[client_id_to_test])
        ) == expcted_result

    def test_search__client_number_exists_returns_list_one_item(self):
        """
        The test validating API does return single client dictionary and
        with the expected key(s) structure.
        """
        client_id_to_test = self.example_expected_valid_result["clientNumber"]
        result = self.fc_api.search(ForestClientIntegrationSearchParmsSchema(forest_client_numbers=[client_id_to_test]))
        assert len(result) == 1
        assert isinstance(result[0], dict)
        result_fc_dict = result[0]
        assert all(key in self.example_expected_valid_result.keys() for key in result_fc_dict.keys())

    # --- test on "search"

    def test_search_not_8_digits_noresult(self):
        """
        Test on not exact 8 digits: []
        """
        not_8_digit_forest_client_numbers=["99999999", "88888888", "00000000"]
        search_param = ForestClientIntegrationSearchParmsSchema(
            forest_client_numbers=not_8_digit_forest_client_numbers
        )
        assert self.fc_api.search(search_param) == []

    def test_search_clients_not_exist_noresult(self):
        """
        Test on clients not exist: []
        """
        not_exist_forest_client_numbers=["99999999", "88888888", "00000000"]
        search_param = ForestClientIntegrationSearchParmsSchema(
            forest_client_numbers=not_exist_forest_client_numbers
        )
        assert self.fc_api.search(search_param) == []

    def test_search_exist_clients_success(self):
        """
        Test on clients exist with success return:
        e.g., [{"clientNumber": "00001011",...},{"clientNumber": "00001012",...}]
        """
        exist_forest_client_numbers=["00001011", "00002011", "00004011"]
        search_param = ForestClientIntegrationSearchParmsSchema(
            forest_client_numbers=exist_forest_client_numbers
        )
        search_results = self.fc_api.search(search_param)
        assert len(search_results) == len(exist_forest_client_numbers)
        self.__verify_fc_common_search_results(search_results, exist_forest_client_numbers)

    def test_search_mix_nonexist_exist_clients(self):
        """
        Test on mix of exist clients and non-exist clients:
        e.g., &id=00001011&id=99999999
        expect just [{"clientNumber": "00001011"}]
        """
        exist_forest_client_numbers=["00001011", "00002011", "00004011"]
        not_exist_forest_client_numbers=["99999999", "88888888", "00000000"]
        search_param = ForestClientIntegrationSearchParmsSchema(
            forest_client_numbers= not_exist_forest_client_numbers + exist_forest_client_numbers
        )
        search_results = self.fc_api.search(search_param)
        assert len(search_results) == len(exist_forest_client_numbers)
        self.__verify_fc_common_search_results(search_results, exist_forest_client_numbers)

    def test_search_more_than_50_clients(self):
        """
        Test API can handle more than 50 clients.
        """
        # Total 51 numbers
        exist_forest_client_numbers=[
            "00000001","00000004","00001011","00001012","00001013","00001014","00001015","00002011","00002012","00002013",
            "00002015","00002017","00002019","00001016","00001018","00001019","00001020","00001021","00001022","00002028",
            "00100000","00100001","00010002","00100003","00100004","00100005","00100006","00100007","00100008","00100009",
            "00100010","00100011","00100012","00100013","00100014","00100015","00100016","00100017","00100018","00100019",
            "00100020","00100021","00100022","00100023","00100024","00100025","00100026","00100027","00100028","00100029",
            "00100030"]
        assert len(exist_forest_client_numbers) > 50
        assert len(set(exist_forest_client_numbers)) == len(exist_forest_client_numbers)  # make sure list having unique numbers.
        search_param = ForestClientIntegrationSearchParmsSchema(
            forest_client_numbers= exist_forest_client_numbers,
            size=len(exist_forest_client_numbers)
        )
        search_results = self.fc_api.search(search_param)
        assert len(search_results) == len(exist_forest_client_numbers)
        self.__verify_fc_common_search_results(search_results, exist_forest_client_numbers)

    def __verify_fc_common_search_results(self, search_results, expect_exist_fc_number):
        assert all(key in self.example_expected_valid_result.keys() for key in search_results[0].keys())
        result_set = {x["clientNumber"] for x in search_results}  # fc api structure confirmation.
        assert result_set == set(expect_exist_fc_number)  # set of unique fc numbers are the same.