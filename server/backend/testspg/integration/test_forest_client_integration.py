

import logging

from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.schemas.forest_client_integration import \
    ForestClientIntegrationSearchParmsSchema
from unittest.mock import Mock

import pytest
import requests

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

    def test_search_not_8_digits_noresult(self):
        """
        Test on not exact 8 digits: []
        """
        not_8_digit_forest_client_numbers=["8", "0001011", "000001011"]
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
        assert isinstance(search_results[0], dict)
        assert all(key in self.example_expected_valid_result.keys() for key in search_results[0].keys())
        result_set = {x["clientNumber"] for x in search_results}  # fc api structure confirmation.
        assert result_set == set(expect_exist_fc_number)  # set of unique fc numbers are the same.


def _make_search_params() -> ForestClientIntegrationSearchParmsSchema:
    """Build a minimal valid search payload used by retry/error tests."""
    return ForestClientIntegrationSearchParmsSchema(
        forest_client_numbers=["00001011"],
        size=1
    )


def _make_success_response(payload):
    """Build a mocked successful requests response object."""
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = payload
    response.elapsed.total_seconds.return_value = 0.01
    return response


class TestForestClientIntegrationServiceRetryAndErrorHandling(object):
    """
    Tests for retry and error handling in ForestClientIntegrationService.
    """

    def test_search_retries_on_connection_error_then_returns_result(self, monkeypatch):
        """
        Test that search retries on ConnectionError and returns successful result on second attempt.
        """
        service = ForestClientIntegrationService()
        expected_payload = [{"clientNumber": "00001011", "clientName": "TEST CLIENT"}]
        successful_response = _make_success_response(expected_payload)
        get_mock = Mock(
            side_effect=[
                requests.exceptions.ConnectionError("connection-error"),
                successful_response,
            ]
        )
        sleep_mock = Mock()
        monkeypatch.setattr(service.session, "get", get_mock)
        monkeypatch.setattr("api.app.integration.forest_client_integration.time.sleep", sleep_mock)

        result = service.search(_make_search_params(), retry_on_timeout=True)

        assert result == expected_payload
        assert get_mock.call_count == 2
        sleep_mock.assert_called_once_with(service.RETRY_DELAY_SECONDS)

    def test_search_retries_on_timeout_and_raises_after_max_attempts(self, monkeypatch, caplog):
        """
        Test that search retries on Timeout, sleeps, and raises after max attempts.
        """
        service = ForestClientIntegrationService()
        error = requests.exceptions.Timeout("timeout")
        get_mock = Mock(side_effect=[error, error])
        sleep_mock = Mock()
        monkeypatch.setattr(service.session, "get", get_mock)
        monkeypatch.setattr("api.app.integration.forest_client_integration.time.sleep", sleep_mock)

        with caplog.at_level(
            logging.ERROR,
            logger="api.app.integration.forest_client_integration"
        ):
            with pytest.raises(requests.exceptions.Timeout):
                service.search(_make_search_params(), retry_on_timeout=True)

        assert get_mock.call_count == 2
        sleep_mock.assert_called_once_with(service.RETRY_DELAY_SECONDS)
        assert "request failed" in caplog.text.lower()
        assert "after 2 attempt(s)" in caplog.text

    def test_search_no_retry_without_flag(self, monkeypatch):
        """
        Test that search does not retry when retry_on_timeout flag is False.
        """
        service = ForestClientIntegrationService()
        error = requests.exceptions.ConnectionError("connection-error")
        get_mock = Mock(side_effect=error)
        sleep_mock = Mock()
        monkeypatch.setattr(service.session, "get", get_mock)
        monkeypatch.setattr("api.app.integration.forest_client_integration.time.sleep", sleep_mock)

        with pytest.raises(requests.exceptions.ConnectionError):
            service.search(_make_search_params(), retry_on_timeout=False)

        assert get_mock.call_count == 1
        sleep_mock.assert_not_called()
