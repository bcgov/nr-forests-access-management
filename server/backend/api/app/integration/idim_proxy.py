from http import HTTPStatus
import logging
from fastapi import HTTPException, Request

import requests
import urllib3
from api.config import config
from requests.adapters import HTTPAdapter

LOGGER = logging.getLogger(__name__)

class IdimProxyService():
    """
    The class is used for making requests to get information from IDIM Proxy API.
    Spec of API:
        test: ?
        prod: ?
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
    original_request: Request

    def __init__(self, original_request):
        self.original_request = original_request # The request should contains necessary header and user/auth token.
        self.api_idim_proxy_url = f"{config.get_idim_proxy_api_baseurl()}/api"
        # TODO: pass encryption piece (maybe use salt as user token and request timestamp), would it be the same?

        self.session = requests.Session()
        self.session.headers.update(self.original_request.headers)

        ## backoff_factor, See ref: https://majornetwork.net/2022/04/handling-retries-in-python-requests/
        retries = urllib3.Retry(total=3, backoff_factor=1, status_forcelist=self.retry_codes)
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def search_idir(self):
        query_params = self.original_request.query_params
        url = f"{self.api_idim_proxy_url}/idir"
        LOGGER.info(f"IdimProxyService search_idir() - url: {url} and param: {query_params}")

        r = self.session.get(url, timeout=self.TIMEOUT, params=query_params)
        r.raise_for_status()
        api_result = r.json()
        LOGGER.debug(f"API result: {api_result}")
        return api_result