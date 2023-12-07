
import copy
import logging

import pytest
from api.app.integration.idim_proxy import IdimProxyService
from api.app.schemas import IdimProxySearchParamIdir, Requester
from requests import HTTPError

LOGGER = logging.getLogger(__name__)


class TestIdimProxyServiceClass(object):
    """
    Testing IdimProxyService class with real remote API calls (TEST environment).
    """
    search_params = IdimProxySearchParamIdir(**{"userId": "ianliu"}) # Valid test IDIR user.

    def setup_class(self):
        # local valid mock requester
        self.requester = Requester(
            ** {
                "cognito_user_id": "dev-idir_e72a12c916a44f39e5dcdffae7@idir",
                "user_name": "IANLIU",
                "user_type": "I",
                "access_roles": ["FAM_ADMIN", "FOM_DEV_ADMIN"]
            }
        )

    def test_verify_init(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester))
        # Quick Verifying for init not empty
        assert idim_proxy_api.api_idim_proxy_url is not None
        api_path = "/api/idim-webservice"
        assert api_path in idim_proxy_api.api_idim_proxy_url
        assert idim_proxy_api.API_KEY is not None
        assert idim_proxy_api.headers["X-API-KEY"] == idim_proxy_api.API_KEY

    def test_no_apikey_error_raised(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester))
        idim_proxy_api.session.headers.update({"X-API-KEY": "Not-A-Valid-Key"})
        with pytest.raises(Exception) as excinfo:
            idim_proxy_api.search_idir(self.search_params)

        assert excinfo.type == HTTPError
        assert excinfo.match("401 Client Error: Unauthorized")

    def test_invalid_requester_error_rasied(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester))
        idim_proxy_api.requester.user_name = "USER_NOT_EXIST"
        with pytest.raises(Exception) as excinfo:
            idim_proxy_api.search_idir(self.search_params)

        assert excinfo.type == HTTPError
        assert excinfo.match("400 Client Error: Bad Request")

    def test_valid_idir_search_pass(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester))
        search_params = copy.deepcopy(self.search_params)
        valid_idir_user = "CMENG"
        search_params.userId = valid_idir_user
        search_result = idim_proxy_api.search_idir(search_params)

        assert search_result['found'] == True
        assert search_result['userId'] == valid_idir_user

    def test_idir_search_user_not_exist_no_user_found(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester))
        search_params = copy.deepcopy(self.search_params)
        not_exists_idir_user = "USERNOTEXISTS"
        search_params.userId = not_exists_idir_user
        search_result = idim_proxy_api.search_idir(search_params)

        assert search_result['found'] == False
        assert search_result['userId'] == None
