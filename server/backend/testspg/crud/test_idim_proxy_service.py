import copy
import logging

import pytest
from api.app.constants import IdimSearchUserParamType
from api.app.integration.idim_proxy import IdimProxyService
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.schemas import (IdimProxyBceidSearchParam, IdimProxySearchParam,
                             Requester)
from fastapi import HTTPException
from requests import HTTPError
from testspg.constants import (TEST_BCEID_REQUESTER_DICT,
                               TEST_IDIR_REQUESTER_DICT,
                               TEST_VALID_BUSINESS_BCEID_USERNAME_ONE,
                               TEST_VALID_BUSINESS_BCEID_USERNAME_TWO)

LOGGER = logging.getLogger(__name__)


class TestIdimProxyServiceClass(object):
    """
    Testing IdimProxyService class with real remote API calls (TEST environment).
    """

    # Valid test IDIR user.
    search_params_idir = IdimProxySearchParam(
        **{"userId": "ianliu"}
    )
    # Valid test Business Bceid user.
    search_params_business_bceid_same_org = IdimProxyBceidSearchParam(
        **{"searchUserBy": IdimSearchUserParamType.USER_ID,
            "searchValue": TEST_VALID_BUSINESS_BCEID_USERNAME_ONE}
    )
    # Valid test Business Bceid user.
    search_params_business_bceid_diff_org = IdimProxyBceidSearchParam(
        **{"searchUserBy": IdimSearchUserParamType.USER_ID,
            "searchValue": TEST_VALID_BUSINESS_BCEID_USERNAME_TWO}
    )

    def setup_class(self):
        # local valid mock requester
        self.requester_idir = Requester(**TEST_IDIR_REQUESTER_DICT)
        self.requester_business_bceid = Requester(**TEST_BCEID_REQUESTER_DICT)

    def test_verify_init(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_idir))
        # Quick Verifying for init not empty
        assert idim_proxy_api.api_idim_proxy_url is not None
        api_path = "/api/idim-webservice"
        assert api_path in idim_proxy_api.api_idim_proxy_url
        assert idim_proxy_api.API_KEY is not None
        assert idim_proxy_api.headers["X-API-KEY"] == idim_proxy_api.API_KEY

    def test_no_apikey_error_raised(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_idir))
        idim_proxy_api.session.headers.update({"X-API-KEY": "Not-A-Valid-Key"})
        with pytest.raises(Exception) as excinfo:
            idim_proxy_api.search_idir(self.search_params_idir)

        assert excinfo.type == HTTPError
        assert excinfo.match("401 Client Error: Unauthorized")

    # --- IDIR requester performs IDIM-Proxy search

    def test_invalid_requester_error_rasied(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_idir))
        idim_proxy_api.requester.user_name = "USER_NOT_EXIST"
        with pytest.raises(Exception) as excinfo:
            idim_proxy_api.search_idir(self.search_params_idir)

        assert excinfo.type == HTTPError
        assert excinfo.match("400 Client Error: Bad Request")

    def test_valid_idir_search_pass(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_idir))
        search_params = copy.deepcopy(self.search_params_idir)
        valid_idir_user = "CMENG"
        search_params.userId = valid_idir_user
        search_result = idim_proxy_api.search_idir(search_params)

        assert search_result["found"] == True
        assert search_result["userId"] == valid_idir_user
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None

    def test_idir_search_user_not_exist_no_user_found(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_idir))
        search_params = copy.deepcopy(self.search_params_idir)
        not_exists_idir_user = "USERNOTEXISTS"
        search_params.userId = not_exists_idir_user
        search_result = idim_proxy_api.search_idir(search_params)

        assert search_result["found"] == False

    # --- BCeID requester performs IDIM-Proxy search

    def test_bceid_search_not_exist_no_user_found(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_business_bceid))
        search_params = copy.deepcopy(self.search_params_business_bceid_same_org)
        not_exists_idir_user = "USERNOTEXISTS"
        search_params.searchValue = not_exists_idir_user
        search_result = idim_proxy_api.search_business_bceid(search_params)

        assert search_result["found"] == False

    def test_valid_bceid_search_pass(self):
        # we use test bceid account for this test, cause we need user's guid, and we don't want to use any IDIR's guid
        # test bceid search for bceid within the same organization
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_business_bceid))
        search_params = copy.deepcopy(self.search_params_business_bceid_same_org)
        search_result = idim_proxy_api.search_business_bceid(search_params)

        assert search_result["found"] == True
        assert search_result["userId"] == TEST_VALID_BUSINESS_BCEID_USERNAME_ONE
        assert search_result["guid"] is not None
        assert search_result["businessGuid"] is not None
        assert search_result["businessLegalName"] is not None
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None

    def test_valid_bceid_diff_org_search_not_allow(self):
        # test bceid search for bceid from a different organization
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_business_bceid))
        search_params = copy.deepcopy(self.search_params_business_bceid_diff_org)

        with pytest.raises(HTTPException) as excinfo:
            idim_proxy_api.search_business_bceid(search_params)

        assert excinfo.type == HTTPException
        assert excinfo.match(ERROR_PERMISSION_REQUIRED)

    # TODO add search with guid tests for BCEID search