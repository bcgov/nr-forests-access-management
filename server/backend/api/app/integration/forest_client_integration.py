import logging
import time
from http import HTTPStatus
from typing import List

import requests
from api.app.constants import ApiInstanceEnv
from api.app.schemas.forest_client_integration import \
    ForestClientIntegrationSearchParmsSchema
from api.config import config

LOGGER = logging.getLogger(__name__)

class ForestClientIntegrationService():
    """
    The class is used for making requests to get information from Forest Client API.
    Api is located at BC API Service Portal: https://api.gov.bc.ca/devportal/api-directory/3179.
    API-key needs to be requested from the portal.
    Spec of API:
        test: https://nr-forest-client-api-test.api.gov.bc.ca/
        prod: https://nr-forest-client-api-prod.api.gov.bc.ca/

    Note! This is external API integration and FAM supports 3 applications environments in PROD.
          For FAM(PROD)-Application(PROD): it will connect to ForestClientAPI PROD instance.
          For rest of application environments (TEST/DEV) in FAM(PROD): it will use TEST instance.
          For FAM environment management relating to the use of external API,
          see ref @FAM Wiki: https://github.com/bcgov/nr-forests-access-management/wiki/Environment-Management
    """
    # https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts
    # https://docs.python-requests.org/en/latest/user/advanced/#timeouts
    TIMEOUT = (5, 10)  # Timeout (connect, read) in seconds.
    # Note: AWS API Gateway has a hard timeout beyong 29 seconds, so the total time -
    # including lambda starts and execution, network latency and plus timeout and retry, should be less than 29 seconds.
    # Two attempts with 5 seconds connect timeout and 10 seconds read timeout, plus 2 seconds retry delay, should be safe
    # on hitting API Gateway timeout.
    RETRY_MAX_ATTEMPTS = 2
    RETRY_DELAY_SECONDS = 2

    def __init__(self, api_instance_env=ApiInstanceEnv.TEST):
        LOGGER.debug(f"ForestClientIntegrationService() use API instance - {api_instance_env}")
        self.api_base_url = config.get_forest_client_api_baseurl(api_instance_env)
        self.api_clients_url = f"{self.api_base_url}/api/clients"
        self.API_TOKEN = config.get_forest_client_api_token(api_instance_env)

        self.headers = {"Accept": "application/json", "X-API-KEY": self.API_TOKEN}

        # See Python: https://requests.readthedocs.io/en/latest/user/advanced/
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search(
        self,
        search_params: ForestClientIntegrationSearchParmsSchema,
        retry_on_timeout: bool = False
    ):
        """
        Find Forest Client(s) with FC API "search"

        :param search_params (ForestClientIntegrationSearchParmsSchema): search params
            for making FC API search request.

        :param retry_on_timeout (bool): if true, retries once when
            requests.exceptions.Timeout or
            requests.exceptions.ConnectionError happens.

        :return (json): Search result as List for a Forest Client information object.
            FC API will return:
            * Not found case (e.g., &id=99999999): 200 []
            * Found case (e.g., &id=00001011&id=00001012): 200 [
                {"clientNumber": "00001011",...},{"clientNumber": "00001012",...}]
            * Invalid format (e.g., &id=kfjencid): 200 []
            * Not exact 8 digits: 200 []
            * With mix of ids found and ids not found (e.g., &id=00001011&id=99999999):
                [{"clientNumber": "00001011"}]
        """
        request_params = (
            f"page={search_params.page}&size={search_params.size}"
            f"{self.__construct_fc_number_search_params(search_params.forest_client_numbers)}"
        )
        url = f"{self.api_clients_url}/search?{request_params}"
        LOGGER.debug(f"ForestClientService search() - url: {url}")

        return self.__do_request(url=url, retry_on_timeout=retry_on_timeout)

    def __do_request(self, url, params=None, retry_on_timeout: bool = False):
        max_attempts = self.RETRY_MAX_ATTEMPTS if retry_on_timeout else 1

        for attempt in range(1, max_attempts + 1):
            try:
                return self.__fetch_json_response(url=url, params=params)

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as rte:
                if self.__retry_request_on_connection_or_timeout(
                    rte=rte,
                    attempt=attempt,
                    max_attempts=max_attempts,
                    url=url
                ):
                    continue

            # Below except catches only HTTPError not general errors like network connection/timeout.
            except requests.exceptions.HTTPError as he:
                return self.__handle_http_error(he)

    def __fetch_json_response(self, url, params=None):
        """Execute request and return JSON response body."""
        response = self.session.get(url, timeout=self.TIMEOUT, params=params)
        response.raise_for_status()

        # !! Don't map and return FamForestClientSchema or object from "scheam.py" as that
        # will create circular dependency issue. let crud to map the result.
        api_result = response.json()
        LOGGER.debug(
            f"FC API result: {api_result}. Took: {response.elapsed.total_seconds()} seconds"
        )
        return api_result

    def __retry_request_on_connection_or_timeout(self, rte, attempt, max_attempts, url):
        """Retry once on timeout/connection errors when enabled; otherwise re-raise."""
        if attempt < max_attempts:
            LOGGER.warning(
                "Forest Client API request failed (%s). Retrying in %s seconds "
                "(attempt %s/%s). url=%s",
                type(rte).__name__,
                self.RETRY_DELAY_SECONDS,
                attempt,
                max_attempts,
                url
            )
            time.sleep(self.RETRY_DELAY_SECONDS)
            return True

        LOGGER.error(
            "Forest Client API request failed (%s) after %s attempt(s). url=%s",
            type(rte).__name__,
            attempt,
            url,
            exc_info=True
        )
        raise rte

    def __handle_http_error(self, he):
        """Return empty result for FC-specific 400/404 search responses; re-raise otherwise."""
        response = he.response
        status_code = response.status_code if response is not None else None
        LOGGER.debug(f"API status code: {status_code}")
        LOGGER.debug(
            "API result: %s",
            (response.content or response.reason)
            if response is not None
            else str(he)
        )

        # For some reason Forest Client API uses (a bit confusing):
        #    - '404' as general "client 'Not Found'", not as conventional http Not Found.
        #
        # Forest Client API returns '400' as "Invalid Client Number"; e.g. /findByClientNumber/abcde0001
        # Howerver FAM 'search' (as string type param) is intended for either 'number' or 'name' search),
        # so if 400, will return empty.
        if ((status_code == HTTPStatus.NOT_FOUND) or (status_code == HTTPStatus.BAD_REQUEST)):
            return []  # return empty for FAM forest client search

        # Else raise error, including 500
        # There is a general error handler, see: requests_http_error_handler
        raise he

    def __construct_fc_number_search_params(self, forest_client_numbers: List[str]):
        # return format as e.g.: &id=00001011&id=00001012
        return "" if not forest_client_numbers else (
            "".join(f"&id={item}" for item in forest_client_numbers)
        )