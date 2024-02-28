import logging

import requests
from api.app.schemas import IdimProxySearchParam, Requester
from api.config import config
from api.app.constants import IDIM_PROXY_ACCOUNT_TYPE_MAP, UserType

LOGGER = logging.getLogger(__name__)


class IdimProxyService:
    """
    The class is used for making requests to search IDIR/BCeID information from IDIM Proxy API.
    See environment setup (local-dev.env) for idim-proxy TEST api-docs.
    """

    TIMEOUT = (5, 10)  # Timeout (connect, read) in seconds.

    def __init__(self, requester: Requester):
        self.requester = requester
        self.api_idim_proxy_url = (
            f"{config.get_idim_proxy_api_baseurl()}/api/idim-webservice"
        )
        self.API_KEY = config.get_idim_proxy_api_key()
        self.headers = {"Accept": "application/json", "X-API-KEY": self.API_KEY}

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search_idir(self, search_params: IdimProxySearchParam):
        """
        Search on IDIR user.
        Note, current idim-proxy only does exact match.
        """
        # query_params to request to idim-proxy
        query_params = vars(search_params)
        query_params.update({"requesterUserId": self.requester.user_name})
        # The proxy allows only "Internal" for this search.
        query_params.update(
            {"requesterAccountTypeCode": IDIM_PROXY_ACCOUNT_TYPE_MAP[UserType.IDIR]}
        )

        url = f"{self.api_idim_proxy_url}/idir"
        LOGGER.info(
            f"IdimProxyService search_idir() - url: {url} and param: {query_params}"
        )

        r = self.session.get(url, timeout=self.TIMEOUT, params=query_params)
        r.raise_for_status()  # There is a general error handler, see: requests_http_error_handler
        api_result = r.json()
        LOGGER.debug(f"API result: {api_result}")
        return api_result

    def search_business_bceid(self, search_params: IdimProxySearchParam):
        """
        Search on Business BCEID user.
        """
        # query_params to request to idim-proxy
        query_params = vars(search_params)
        query_params.update({"requesterUserGuid": self.requester.user_guid})
        query_params.update(
            {
                "requesterAccountTypeCode": IDIM_PROXY_ACCOUNT_TYPE_MAP[
                    self.requester.user_type_code
                ]
            }
        )

        url = f"{self.api_idim_proxy_url}/bceid"
        LOGGER.info(
            f"IdimProxyService search_bceid() - url: {url} and param: {query_params}"
        )

        r = self.session.get(url, timeout=self.TIMEOUT, params=query_params)
        r.raise_for_status()  # There is a general error handler, see: requests_http_error_handler
        api_result = r.json()
        LOGGER.debug(f"API result: {api_result}")
        return api_result
