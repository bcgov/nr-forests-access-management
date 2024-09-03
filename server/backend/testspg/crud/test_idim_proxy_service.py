import os
import copy
import logging

import pytest
from api.app.constants import IdimSearchUserParamType
from api.app.integration.idim_proxy import IdimProxyService
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.schemas import (
    IdimProxyBceidSearchParamSchema,
    IdimProxySearchParamSchema,
    RequesterSchema,
)
from fastapi import HTTPException
from requests import HTTPError
from testspg.constants import (
    TEST_BCEID_REQUESTER_DICT,
    TEST_IDIR_REQUESTER_DICT,
    USER_GUID_BCEID_LOAD_3_TEST,
    USER_GUID_BCEID_LOAD_3_TEST_CHILD_1,
    USER_NAME_BCEID_LOAD_2_TEST,
    USER_NAME_BCEID_LOAD_3_TEST,
    USER_NAME_BCEID_LOAD_3_TEST_CHILD_1,
)

LOGGER = logging.getLogger(__name__)

TEST_IDIR_USER_GUID = os.environ.get("TEST_IDIR_USER_GUID")


class TestIdimProxyServiceClass(object):
    """
    Testing IdimProxyService class with real remote API calls (TEST environment).
    """

    # Valid test IDIR user.
    search_params_idir = IdimProxySearchParamSchema(**{"userId": "ianliu"})
    # Valid test Business Bceid user
    search_params_business_bceid_same_org = IdimProxyBceidSearchParamSchema(
        **{
            "searchUserBy": IdimSearchUserParamType.USER_ID,
            "searchValue": USER_NAME_BCEID_LOAD_3_TEST_CHILD_1,
        }
    )
    # Valid test Business Bceid user.
    search_params_business_bceid_diff_org = IdimProxyBceidSearchParamSchema(
        **{
            "searchUserBy": IdimSearchUserParamType.USER_ID,
            "searchValue": USER_NAME_BCEID_LOAD_2_TEST,
        }
    )

    def setup_class(self):
        # local valid mock RequesterSchema
        self.requester_idir = RequesterSchema(**TEST_IDIR_REQUESTER_DICT)
        self.requester_idir.user_guid = TEST_IDIR_USER_GUID

        # This tester uses "LOAD-3-TEST"
        self.requester_business_bceid = RequesterSchema(**TEST_BCEID_REQUESTER_DICT)

    def test_verify_init(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)
        # Quick Verifying for init not empty
        assert idim_proxy_api.api_idim_proxy_url is not None
        api_path = "/api/idim-webservice"
        assert api_path in idim_proxy_api.api_idim_proxy_url
        assert idim_proxy_api.API_KEY is not None
        assert idim_proxy_api.headers["X-API-KEY"] == idim_proxy_api.API_KEY

    def test_no_apikey_error_raised(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)
        idim_proxy_api.session.headers.update({"X-API-KEY": "Not-A-Valid-Key"})
        with pytest.raises(Exception) as excinfo:
            idim_proxy_api.search_idir(self.search_params_idir)

        assert excinfo.type == HTTPError
        assert excinfo.match("401 Client Error: Unauthorized")

    # --- Performs search_idir user (This is only for IDIR RequesterSchema) ---

    def test_search_idir__invalid_idir_requester_error_rasied(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_idir))
        idim_proxy_api.RequesterSchema.user_name = "USER_NOT_EXIST"
        with pytest.raises(Exception) as excinfo:
            idim_proxy_api.search_idir(self.search_params_idir)

        assert excinfo.type == HTTPError
        assert excinfo.match("400 Client Error: Bad Request")

    def test_search_idir__valid_idir_search_pass(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)
        search_params = copy.deepcopy(self.search_params_idir)
        valid_idir_user = "CMENG"
        search_params.userId = valid_idir_user
        search_result = idim_proxy_api.search_idir(search_params)

        assert search_result["found"] == True
        assert search_result["userId"] == valid_idir_user
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None

    def test_search_idir__user_not_exist_no_user_found(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)
        search_params = copy.deepcopy(self.search_params_idir)
        not_exists_idir_user = "USERNOTEXISTS"
        search_params.userId = not_exists_idir_user
        search_result = idim_proxy_api.search_idir(search_params)

        assert search_result["found"] == False

    # --- Performs search_business_bceid user (IDIR RequesterSchema/BCeID RequesterSchema) ---

    def test_search_bceid__user_not_exist_not_found(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)
        search_params = copy.deepcopy(self.search_params_business_bceid_same_org)
        not_exists_idir_user = "USERNOTEXISTS"
        search_params.searchValue = not_exists_idir_user
        search_result = idim_proxy_api.search_business_bceid(search_params)

        assert search_result["found"] == False

    def test_search_bceid__idir_requester_by_userid_search_pass(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_idir))

        # for IDIR RequesterSchema, it does not matter the "business organization" for BCeID user.
        search_result = idim_proxy_api.search_business_bceid(
            self.search_params_business_bceid_same_org
        )

        assert search_result["found"]
        assert search_result["userId"] == USER_NAME_BCEID_LOAD_3_TEST_CHILD_1
        assert search_result["guid"] is not None
        assert search_result["businessGuid"] is not None
        assert search_result["businessLegalName"] is not None
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None

    def test_search_bceid__bceid_requester_by_userid_same_org_search_pass(self):
        # we use test bceid account for this test, cause we need user's guid, and we don't want to use any IDIR's guid
        # test bceid search for bceid within the same organization
        idim_proxy_api = IdimProxyService(self.requester_business_bceid)

        # This search_params uses "TEST-3-LOAD-CHILD-1", same org with "LOAD-3-TEST"
        search_result = idim_proxy_api.search_business_bceid(
            search_params=self.search_params_business_bceid_same_org
        )

        assert search_result["found"]
        assert search_result["userId"] == USER_NAME_BCEID_LOAD_3_TEST_CHILD_1
        assert search_result["guid"] is not None
        assert search_result["businessGuid"] is not None
        assert search_result["businessLegalName"] is not None
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None

    def test_search_bceid__bceid_requester_by_userid_diff_org_search_not_allow(self):
        # test bceid search for bceid from a different organization
        idim_proxy_api = IdimProxyService(self.requester_business_bceid)

        with pytest.raises(HTTPException) as excinfo:
            idim_proxy_api.search_business_bceid(
                search_params=self.search_params_business_bceid_diff_org
            )

        assert excinfo.type == HTTPException
        assert excinfo.match(ERROR_PERMISSION_REQUIRED)

    def test_search_bceid__idir_requester_by_user_guid_search_pass(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)

        # for IDIR RequesterSchema, it does not matter the "business organization" for BCeID user.
        search_params = IdimProxyBceidSearchParamSchema(
            **{
                "searchUserBy": IdimSearchUserParamType.USER_GUID,
                "searchValue": USER_GUID_BCEID_LOAD_3_TEST,
            }
        )
        search_result = idim_proxy_api.search_business_bceid(search_params)

        assert search_result["found"]
        assert search_result["userId"] == USER_NAME_BCEID_LOAD_3_TEST
        assert search_result["guid"] is not None
        assert search_result["businessGuid"] is not None
        assert search_result["businessLegalName"] is not None
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None

    @pytest.mark.skip(
        reason="Search BCeID by user_guid is not enabled. Enable this test when ready."
    )
    def test_search_bceid__bceid_requester_by_user_guid_same_org_search_pass(self):
        # business bceid RequesterSchema
        idim_proxy_api = IdimProxyService(self.requester_business_bceid)

        # This search_params uses "TEST-3-LOAD-CHILD-1", same org with "LOAD-3-TEST"
        search_params = IdimProxyBceidSearchParamSchema(
            **{
                "searchUserBy": IdimSearchUserParamType.USER_GUID,
                "searchValue": USER_GUID_BCEID_LOAD_3_TEST_CHILD_1,
            }
        )
        search_result = idim_proxy_api.search_business_bceid(search_params)

        assert search_result["found"]
        assert search_result["userId"] == USER_NAME_BCEID_LOAD_3_TEST_CHILD_1
        assert search_result["guid"] is not None
        assert search_result["businessGuid"] is not None
        assert search_result["businessLegalName"] is not None
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None
