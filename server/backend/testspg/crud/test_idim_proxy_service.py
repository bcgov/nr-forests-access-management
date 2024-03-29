import copy
import logging
import os
from requests import HTTPError
import pytest

from api.app.integration.idim_proxy import IdimProxyService
from api.app.schemas import IdimProxySearchParam, Requester
from testspg.constants import TEST_IDIR_REQUESTER_DICT


LOGGER = logging.getLogger(__name__)


class TestIdimProxyServiceClass(object):
    """
    Testing IdimProxyService class with real remote API calls (TEST environment).
    """

    TEST_BUSINESS_BCEID_USERNAME = "LOAD-2-TEST"
    search_params = IdimProxySearchParam(
        **{"userId": "ianliu"}
    )  # Valid test IDIR user.
    search_params_business_bceid = IdimProxySearchParam(
        **{"userId": TEST_BUSINESS_BCEID_USERNAME}
    )  # Valid test Business Bceid user.

    def setup_class(self):
        # local valid mock requester
        self.requester = Requester(**TEST_IDIR_REQUESTER_DICT)

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

        assert search_result["found"] == True
        assert search_result["userId"] == valid_idir_user
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None

    def test_idir_search_user_not_exist_no_user_found(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester))
        search_params = copy.deepcopy(self.search_params)
        not_exists_idir_user = "USERNOTEXISTS"
        search_params.userId = not_exists_idir_user
        search_result = idim_proxy_api.search_idir(search_params)

        assert search_result["found"] == False

    @pytest.mark.skip(
        reason="need idir user guid to run this test, switch to use bceid search bceid later"
    )
    def test_bceid_search_not_exist_no_user_found(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester))
        search_params = copy.deepcopy(self.search_params_business_bceid)
        not_exists_idir_user = "USERNOTEXISTS"
        search_params.userId = not_exists_idir_user
        search_result = idim_proxy_api.search_business_bceid(search_params)

        assert search_result["found"] == False

    @pytest.mark.skip(
        reason="need idir user guid to run this test, switch to use bceid search bceid later"
    )
    def test_valid_bceid_search_pass(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester))
        search_params = copy.deepcopy(self.search_params_business_bceid)
        search_result = idim_proxy_api.search_business_bceid(search_params)

        assert search_result["found"] == True
        assert search_result["userId"] == self.TEST_BUSINESS_BCEID_USERNAME
        assert search_result["guid"] is not None
        assert search_result["businessGuid"] is not None
        assert search_result["businessLegalName"] is not None
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None
