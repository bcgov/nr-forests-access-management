import logging
from http import HTTPStatus

import requests
from api.app.constants import (IDIM_PROXY_ACCOUNT_TYPE_MAP, ApiInstanceEnv,
                               UserType)
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.schemas import (IdimProxyBceidSearchParamSchema,
                             IdimProxySearchParamSchema, RequesterSchema)
from api.config import config
from fastapi import HTTPException

LOGGER = logging.getLogger(__name__)


class IdimProxyService:
    """
    The class is used for making requests to search IDIR/BCeID information from IDIM Proxy API.
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

    def search_idir(self, search_params: IdimProxySearchParamSchema):
        """
        Search on IDIR user.
        Note, current idim-proxy only does exact match.
        """

        """
        TODO: original IDIR search method. Temporarily commented out   # noqa NOSONAR
        IDIM Consulting currently breaks the production IDIR looks up IDIR user scenario.

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
        """

        # --- new temporary IDIR call to fix production issue (see above old code comment)
        query_params = vars(search_params)
        query_params.update({"requesterUserGuid": self.requester.user_guid})
        url = f"{self.api_idim_proxy_url}/idir-account-detail"
        LOGGER.info(
            f"IdimProxyService search_idir() - url: {url} and param: {query_params}"
        )
        # --- end new temporary IDIR call to fix production issue

        r = self.session.get(url, timeout=self.TIMEOUT, params=query_params)
        r.raise_for_status()  # There is a general error handler, see: requests_http_error_handler
        api_result = r.json()
        LOGGER.debug(f"API result: {api_result}")
        return api_result

    def search_business_bceid(self, search_params: IdimProxyBceidSearchParamSchema):
        """
        Search on Business BCEID user.
        This search can be perfomed by IDIR requester or BCeID requester by passing "user_guid" to
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
            f"IdimProxyService search_business_bceid() - url: {url} and param: {query_params}"
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
