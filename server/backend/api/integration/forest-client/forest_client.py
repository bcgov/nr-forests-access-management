import logging

from api.config import config
from pydantic import constr
from requests import Session

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
        self.api_base_url = config.get_forest_client_api_baseurl()
        self.api_clients_url = f"{self.apiBaseUri}/api/clients"
        self.API_TOKEN = config.get_forest_client_api_token()
        self.headers = {"accepts": "application/json", "X-API-KEY": self.API_TOKEN}

        # See Python: https://requests.readthedocs.io/en/latest/user/advanced/
        self.session = Session()
        self.session.headers.update(self.headers)

    def find_by_client_number(self, p_client_number: constr(min_length=8, max_length=8)):
        """
        Find Forest Client(s) information based on p_client_number search query field.

        :param p_client_number: Forest Client Number string (8 digits).
                                Note! Current Forest Client API can only do exact match.
                                '/api/clients/findByClientNumber/{clientNumber}'
        :return: Search result for a Forest Client information object.
        """
        uri = f"{self.api_clients_url}/findByClientNumber/{p_client_number}"
        LOGGER.debug(f"ForestClient find_by_client_number() - uri: {uri}")
        r = self.session.get(uri)
        return r.json()
