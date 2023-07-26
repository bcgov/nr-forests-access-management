import logging
from http import HTTPStatus

import requests
import urllib3
from api.app.requester import Requester
from api.app.schemas import IdimProxySearchParamIdir
from api.config import config
from requests.adapters import HTTPAdapter

LOGGER = logging.getLogger(__name__)

REQUESTER_ACCOUNT_TYPE_INTERNAL = "Internal"

class IdimProxyService():
    """
    The class is used for making requests to search IDIR/BCeID information from IDIM Proxy API.
    See environment setup (local-dev.env) for idim-proxy TEST api-docs.
    """
    TIMEOUT = (4, 20) # Timeout (connect, read) in seconds.
    RETRY = 3
    retry_codes = [
        HTTPStatus.TOO_MANY_REQUESTS, # 429
        HTTPStatus.INTERNAL_SERVER_ERROR, # 500
        HTTPStatus.BAD_GATEWAY, # 502
        HTTPStatus.SERVICE_UNAVAILABLE, # 503
        HTTPStatus.GATEWAY_TIMEOUT, # 504
    ]

    def __init__(self, requester: Requester):
        self.requester = requester
        self.api_idim_proxy_url = f"{config.get_idim_proxy_api_baseurl()}/api"
        self.API_KEY = config.get_idim_proxy_api_key()
        self.headers = {"Accept": "application/json", "X-API-KEY": self.API_KEY}

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        ## backoff_factor, See ref: https://majornetwork.net/2022/04/handling-retries-in-python-requests/
        retries = urllib3.Retry(total=3, backoff_factor=1, status_forcelist=self.retry_codes)
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def search_idir(self, search_params: IdimProxySearchParamIdir):
        """
        Search on IDIR user.
        Note, current idim-proxy only does exact match.
        """
        # query_params to request to idim-proxy
        query_params = vars(search_params)
        query_params.update({"requesterUserId": self.requester.user_name})
        # The proxy allows only "Internal" for this search.
        query_params.update({"requesterAccountTypeCode": REQUESTER_ACCOUNT_TYPE_INTERNAL})

        url = f"{self.api_idim_proxy_url}/idim-webservice/idir"
        LOGGER.info(f"IdimProxyService search_idir() - url: {url} and param: {query_params}")

        r = self.session.get(url, timeout=self.TIMEOUT, params=query_params)
        r.raise_for_status()
        api_result = r.json()
        LOGGER.debug(f"API result: {api_result}")
        return api_result