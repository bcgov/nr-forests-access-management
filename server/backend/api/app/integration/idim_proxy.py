import logging
import time
from http import HTTPStatus

import requests
from api.app.constants import (IDIM_PROXY_ACCOUNT_TYPE_MAP, ApiInstanceEnv,
                               UserType)
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.schemas import (
    IdimProxyBceidSearchParamSchema,
    IdimProxySearchParamSchema,
    RequesterSchema,
)
from api.app.schemas.idim_proxy_idir_users_search import (
    IdimProxyIdirUsersSearchParamReqSchema,
    IdimProxyIdirUsersSearchResSchema,
)
from api.config import config
from fastapi import HTTPException

LOGGER = logging.getLogger(__name__)


class IdimProxyService:
    """
    The class is used for making requests to lookup/search IDIR/BCeID information from IDIM Proxy API.
    See environment setup (local-dev.env) for idim-proxy configuration.
    Note:
        Currently IDIM Proxy is configured to use the same api key value.
        So there is no need for different key based on environment.

    Note! This is external API integration and FAM supports 3 applications environments in PROD.
        For FAM(PROD)-Application(PROD): it will connect to IdimProxy API PROD instance.
        For rest of application environments (TEST/DEV) in FAM(PROD): it will use TEST instance.
        For FAM environment management relating to the use of external API,
        see ref @FAM Wiki: https://github.com/bcgov/nr-forests-access-management/wiki/Environment-Management
    """

    TIMEOUT = (5, 10)  # Timeout (connect, read) in seconds.

    def __init__(
        self,
        requester: RequesterSchema,
        api_instance_env: ApiInstanceEnv = ApiInstanceEnv.TEST,
    ):
        self.requester = requester
        # by default use test idim proxy url if not specify the api instance enviornment
        self.api_idim_proxy_url = (
            f"{config.get_idim_proxy_api_baseurl(api_instance_env)}/api/idim-webservice"
        )
        self.API_KEY = config.get_idim_proxy_api_key()
        self.headers = {"Accept": "application/json", "X-API-KEY": self.API_KEY}

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def lookup_idir(self, search_params: IdimProxySearchParamSchema):
        """
        Lookup single IDIR user.
        Note, current idim-proxy only does exact match.
        """
        query_params = vars(search_params)
        query_params.update({"requesterUserGuid": self.requester.user_guid})
        url = f"{self.api_idim_proxy_url}/idir-account-detail"
        LOGGER.info(
            f"IdimProxyService lookup_idir() - url: {url} and param: {query_params}"
        )

        r = self.session.get(url, timeout=self.TIMEOUT, params=query_params)
        r.raise_for_status()  # There is a general error handler, see: requests_http_error_handler
        api_result = r.json()
        LOGGER.debug(f"API result: {api_result}")
        return api_result

    def lookup_business_bceid(self, search_params: IdimProxyBceidSearchParamSchema):
        """
        Lookup single Business BCEID user.
        This lookup can be performed by IDIR requester or BCeID requester by passing "user_guid" to
        "requesterUserGuid".
        search_param: is of type "IdimProxyBceidSearchParamSchema" and can be 'searchUserBy'
            - "userId" or
            - "userGuid" (preferred)
        """
        # query_params to request to idim-proxy, vars(search_params) returns a dict of the search_params
        query_params = vars(search_params)
        query_params.update({"requesterUserGuid": self.requester.user_guid})
        query_params.update(
            {
                "requesterAccountTypeCode": IDIM_PROXY_ACCOUNT_TYPE_MAP[
                    self.requester.user_type_code
                ]
            }
        )

        url = f"{self.api_idim_proxy_url}/businessBceid"
        LOGGER.info(
            f"IdimProxyService lookup_business_bceid() - url: {url} and param: {query_params}"
        )

        r = self.session.get(url, timeout=self.TIMEOUT, params=query_params)
        r.raise_for_status()  # There is a general error handler, see: requests_http_error_handler
        api_result = r.json()

        if (
            api_result.get("found") == True
            and self.requester.user_type_code == UserType.BCEID
            and self.requester.business_guid != api_result.get("businessGuid")
        ):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail={
                    "code": ERROR_PERMISSION_REQUIRED,
                    "description": "Operation requires business bceid users to be within the same organization",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        LOGGER.debug(f"API result: {api_result}")
        return api_result

    def search_idir_users(
        self, search_params: IdimProxyIdirUsersSearchParamReqSchema
    ):
        """
        Search IDIR users with optional partial-match query fields.
        """
        query_params = search_params.model_dump(exclude_none=True)
        body = {"requesterUserGuid": self.requester.user_guid}
        url = f"{self.api_idim_proxy_url}/idir-users/search"

        LOGGER.info(
            "IdimProxyService search_idir_users() - url: %s and query: %s",
            url,
            query_params,
        )

        start = time.perf_counter()
        try:
            r = self.session.post(
                url,
                timeout=self.TIMEOUT,
                params=query_params,
                json=body,
            )
            r.raise_for_status()
            api_result = IdimProxyIdirUsersSearchResSchema(**r.json()).model_dump()
            LOGGER.debug("API result: %s", api_result)
            return api_result
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            LOGGER.info(
                "IdimProxyService search_idir_users() completed in %.2f ms for url: %s",
                elapsed_ms,
                url,
            )
