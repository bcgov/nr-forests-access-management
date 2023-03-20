import logging

from requests import Session
from api.config import config

LOGGER = logging.getLogger(__name__)


class ForestClient:
    """
    The class is used for making requests to get information from Forest Client API.
    Api is located at BC API Service Portal: https://api.gov.bc.ca/devportal/api-directory/3179.
    API-key needs to be requested from the portal.
    Spec of API:
        test: https://nr-forest-client-api-test.api.gov.bc.ca/
        prod: https://nr-forest-client-api-prod.api.gov.bc.ca/
    """
    def __init__(self):
        self.apiBaseUri = config.get_forest_client_api_baseurl()
        self.API_TOKEN = config.get_forest_client_api_token()
        self.headers = {"accepts": "application/json", "X-API-KEY": self.API_TOKEN}

        # See Python: https://requests.readthedocs.io/en/latest/user/advanced/
        self.session = Session()
        self.session.headers.update(self.headers)

    def get_by_client_number(self, p_client_number: str):
        """
        Find Forest Client(s) information based on p_client_number search query field.

        :param p_client_number: Forest Client Number string (8 digits); can be partial.
                                Note! Current Forest Client API can only do exact match.
                                '/api/clients/findByClientNumber/{clientNumber}'
        :return: Search result for list of Forest Client(s) information object.
        """
        uri = f"{self.apiBaseUri}/api/clients/findByClientNumber/{p_client_number}"
        LOGGER.debug(f"ForestClient get_by_client_number() - uri: {uri}")
        r = self.session.get(uri)
        return r.json()
