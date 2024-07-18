import logging
from http import HTTPStatus

import requests
from api.app.constants import AppEnv
from api.config import config

LOGGER = logging.getLogger(__name__)


class ForestClientService():
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

    def __init__(self, app_env: AppEnv = AppEnv.APP_ENV_TYPE_TEST):
        # api instance to use.
        self.apiInstanceEnv = config.use_api_instance_by_app_env(app_env)
        LOGGER.debug(f"ForestClientService() use API instance - {self.apiInstanceEnv}")

        self.api_base_url = config.get_forest_client_api_baseurl(self.apiInstanceEnv)
        self.api_clients_url = f"{self.api_base_url}/api/clients"
        self.API_TOKEN = config.get_forest_client_api_token(self.apiInstanceEnv)

        self.headers = {"Accept": "application/json", "X-API-KEY": self.API_TOKEN}

        # See Python: https://requests.readthedocs.io/en/latest/user/advanced/
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def find_by_client_number(self, p_client_number: str):
        """
        Find Forest Client(s) information based on p_client_number search query field.

        :param p_client_number: Forest Client Number string (8 digits).
                                Note! Current Forest Client API can only do exact match.
                                '/api/clients/findByClientNumber/{clientNumber}'
        :return: Search result as List for a Forest Client information object.
                 Current Forest Client API returns exact one result or http status
                 other than 200 with message content. The intent for FAM search is for
                 wild card search and Forest Client API could be capable of doing that
                 in next version.
        """
        url = f"{self.api_clients_url}/findByClientNumber/{p_client_number}"
        LOGGER.debug(f"ForestClientService find_by_client_number() - url: {url}")

        try:
            r = self.session.get(url, timeout=self.TIMEOUT)
            r.raise_for_status()
            # !! Don't map and return schema.FamForestClient or object from "scheam.py" as that
            # will create circular dependency issue. let crud to map the result.
            api_result = r.json()
            LOGGER.debug(f"API result: {api_result}")
            return [api_result]

        # Below except catches only HTTPError not general errors like network connection/timeout.
        except requests.exceptions.HTTPError as he:
            status_code = r.status_code
            LOGGER.debug(f"API status code: {status_code}")
            LOGGER.debug(f"API result: {r.content or r.reason}")

            # For some reason Forest Client API uses (a bit confusing):
            #    - '404' as general "client 'Not Found'", not as conventional http Not Found.
            #
            # Forest Client API returns '400' as "Invalid Client Number"; e.g. /findByClientNumber/abcde0001
            # Howerver FAM 'search' (as string type param) is intended for either 'number' or 'name' search),
            # so if 400, will return empty.
            if ((status_code == HTTPStatus.NOT_FOUND) or (status_code == HTTPStatus.BAD_REQUEST)):
                return [] # return empty for FAM forest client search

            # Else raise error, including 500
            # There is a general error handler, see: requests_http_error_handler
            raise he