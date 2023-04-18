import logging
from http import HTTPStatus

import requests
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
    """
    def __init__(self):
        self.api_base_url = config.get_forest_client_api_baseurl()
        self.api_clients_url = f"{self.api_base_url}/api/clients"
        self.API_TOKEN = config.get_forest_client_api_token()
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
        r = self.session.get(url)
        status_code = r.status_code
        api_result = r.json() if r.status_code == HTTPStatus.OK else r.content
        LOGGER.debug(f"API status code: {status_code}")
        LOGGER.debug(f"API result: {api_result}")

        # !! Don't map and return schema.FamForestClient or object from "scheam.py" as that
        # will create circular dependency issue. let crud to map the result.
        api_result = []
        if (r.status_code == HTTPStatus.OK):
            api_result = [r.json()]
        return api_result
