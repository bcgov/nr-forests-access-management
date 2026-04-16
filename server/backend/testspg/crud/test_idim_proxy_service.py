import copy
import logging
import os

import pytest
from unittest.mock import MagicMock, patch
from api.app.constants import IdimSearchUserParamType
from api.app.integration.idim_proxy import IdimProxyService
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.schemas import (IdimProxyBceidSearchParamSchema,
                             IdimProxySearchParamSchema, RequesterSchema)
from api.app.schemas.idim_proxy_idir_users_search import (
    IdimProxyIdirUserSearchItemResSchema,
    IdimProxyIdirUsersSearchParamReqSchema,
    IdimProxyIdirUsersSearchResSchema,
    IdimSearchMatchMode,
)
from fastapi import HTTPException
from requests import HTTPError
from testspg.constants import (TEST_BCEID_REQUESTER_DICT,
                               TEST_IDIR_REQUESTER_DICT,
                               USER_GUID_BCEID_LOAD_3_TEST,
                               USER_GUID_BCEID_LOAD_3_TEST_CHILD_1,
                               USER_NAME_BCEID_LOAD_2_TEST,
                               USER_NAME_BCEID_LOAD_3_TEST,
                               USER_NAME_BCEID_LOAD_3_TEST_CHILD_1)

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
            idim_proxy_api.lookup_idir(self.search_params_idir)

        assert excinfo.type == HTTPError
        assert excinfo.match("401 Client Error: Unauthorized")

    # --- Performs lookup_idir user (This is only for IDIR requester) ---

    @pytest.mark.skip(
        reason="Temporary IDIR search production fix break this test. Fix or enable later."
    )
    def test_lookup_idir__invalid_idir_requester_error_rasied(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_idir))
        idim_proxy_api.requester.user_name = "USER_NOT_EXIST"
        with pytest.raises(Exception) as excinfo:
            idim_proxy_api.lookup_idir(self.search_params_idir)

        assert excinfo.type == HTTPError
        assert excinfo.match("400 Client Error: Bad Request")

    def test_lookup_idir__valid_idir_search_pass(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)
        search_params = copy.deepcopy(self.search_params_idir)
        valid_idir_user = "MOF_FAMD"
        search_params.userId = valid_idir_user
        search_result = idim_proxy_api.lookup_idir(search_params)

        assert search_result["found"] == True
        assert search_result["userId"] == valid_idir_user
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None

    def test_lookup_idir__user_not_exist_no_user_found(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)
        search_params = copy.deepcopy(self.search_params_idir)
        not_exists_idir_user = "USERNOTEXISTS"
        search_params.userId = not_exists_idir_user
        search_result = idim_proxy_api.lookup_idir(search_params)

        assert search_result["found"] == False

    # --- Performs lookup_business_bceid user (IDIR Requester/BCeID Requester) ---

    def test_lookup_business_bceid__idir_requester_user_not_exist_not_found(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)
        search_params = copy.deepcopy(self.search_params_business_bceid_same_org)
        search_params.searchValue = "USERNOTEXISTS"
        search_result = idim_proxy_api.lookup_business_bceid(search_params)

        assert search_result["found"] == False
        assert search_result["userId"] == search_params.searchValue

    def test_lookup_business_bceid__bceid_requester_user_not_exist_not_found(self):
        # test bceid search for unknow bceid
        idim_proxy_api = IdimProxyService(self.requester_business_bceid)
        search_params = copy.deepcopy(self.search_params_business_bceid_same_org)
        search_params.searchValue = "USERNOTEXISTS"
        search_result = idim_proxy_api.lookup_business_bceid(search_params)

        assert search_result["found"] == False
        assert search_result["userId"] == search_params.searchValue

    def test_lookup_business_bceid__idir_requester_by_userid_search_pass(self):
        idim_proxy_api = IdimProxyService(copy.deepcopy(self.requester_idir))

        # for IDIR Requester, it does not matter the "business organization" for BCeID user.
        search_result = idim_proxy_api.lookup_business_bceid(
            self.search_params_business_bceid_same_org
        )

        assert search_result["found"]
        assert search_result["userId"] == USER_NAME_BCEID_LOAD_3_TEST_CHILD_1
        assert search_result["guid"] is not None
        assert search_result["businessGuid"] is not None
        assert search_result["businessLegalName"] is not None
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None

    def test_lookup_business_bceid__bceid_requester_by_userid_same_org_search_pass(self):
        # we use test bceid account for this test, cause we need user's guid, and we don't want to use any IDIR's guid
        # test bceid search for bceid within the same organization
        idim_proxy_api = IdimProxyService(self.requester_business_bceid)

        # This search_params uses "TEST-3-LOAD-CHILD-1", same org with "LOAD-3-TEST"
        search_result = idim_proxy_api.lookup_business_bceid(
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
            idim_proxy_api.lookup_business_bceid(
                search_params=self.search_params_business_bceid_diff_org
            )

        assert excinfo.type == HTTPException
        assert excinfo.match(ERROR_PERMISSION_REQUIRED)

    def test_search_bceid__idir_requester_by_user_guid_search_pass(self):
        idim_proxy_api = IdimProxyService(self.requester_idir)

        # for IDIR Requester, it does not matter the "business organization" for BCeID user.
        search_params = IdimProxyBceidSearchParamSchema(
            **{
                "searchUserBy": IdimSearchUserParamType.USER_GUID,
                "searchValue": USER_GUID_BCEID_LOAD_3_TEST,
            }
        )
        search_result = idim_proxy_api.lookup_business_bceid(search_params)

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
        # business bceid Requester
        idim_proxy_api = IdimProxyService(self.requester_business_bceid)

        # This search_params uses "TEST-3-LOAD-CHILD-1", same org with "LOAD-3-TEST"
        search_params = IdimProxyBceidSearchParamSchema(
            **{
                "searchUserBy": IdimSearchUserParamType.USER_GUID,
                "searchValue": USER_GUID_BCEID_LOAD_3_TEST_CHILD_1,
            }
        )
        search_result = idim_proxy_api.lookup_business_bceid(search_params)

        assert search_result["found"]
        assert search_result["userId"] == USER_NAME_BCEID_LOAD_3_TEST_CHILD_1
        assert search_result["guid"] is not None
        assert search_result["businessGuid"] is not None
        assert search_result["businessLegalName"] is not None
        assert search_result["firstName"] is not None
        assert search_result["lastName"] is not None


# ============================================================================
# Unit test cases for search_idir_users method
# ============================================================================
class TestIdimProxyServiceSearchIdirUsers:
    """
    Testing IdimProxyService.search_idir_users method with mocked HTTP responses.
    """

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.requester = RequesterSchema(**TEST_IDIR_REQUESTER_DICT)
        self.requester.user_guid = "TESTGUID12345678901234567890ABCD"

    def test_search_idir_users_success_returns_json(self):
        """Test successful search returns expected JSON structure."""
        idim_proxy_api = IdimProxyService(self.requester)
        search_params = IdimProxyIdirUsersSearchParamReqSchema(firstName="John")

        mock_response = {
            "totalItems": 2,
            "pageSize": 50,
            "items": [
                {
                    "userId": "john.doe",
                    "guid": "12345678123412341234123456789012",
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@gov.bc.ca",
                },
                {
                    "userId": "john.smith",
                    "guid": "87654321432143214321210987654321",
                    "firstName": "John",
                    "lastName": "Smith",
                    "email": "john.smith@gov.bc.ca",
                },
            ],
        }

        with patch.object(idim_proxy_api.session, "post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            result = idim_proxy_api.search_idir_users(search_params)

            assert result["totalItems"] == 2
            assert result["pageSize"] == 50
            assert len(result["items"]) == 2
            assert result["items"][0]["userId"] == "john.doe"
            assert result["items"][1]["userId"] == "john.smith"

    def test_search_idir_users_success_with_empty_items(self):
        """Test successful search with no results returns empty items list."""
        idim_proxy_api = IdimProxyService(self.requester)
        search_params = IdimProxyIdirUsersSearchParamReqSchema(firstName="NONEXISTENT")

        mock_response = {
            "totalItems": 0,
            "pageSize": 50,
            "items": [],
        }

        with patch.object(idim_proxy_api.session, "post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            result = idim_proxy_api.search_idir_users(search_params)

            assert result["totalItems"] == 0
            assert result["pageSize"] == 50
            assert len(result["items"]) == 0

    def test_search_idir_users_uses_post_with_body_and_query(self):
        """Test that POST request is made with correct body and query parameters."""
        idim_proxy_api = IdimProxyService(self.requester)
        search_params = IdimProxyIdirUsersSearchParamReqSchema(
            firstName="John",
            lastName="Doe",
            firstNameMatchMode=IdimSearchMatchMode.CONTAINS,
            pageSize=25,
        )

        mock_response = {
            "totalItems": 1,
            "pageSize": 25,
            "items": [],
        }

        with patch.object(idim_proxy_api.session, "post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            idim_proxy_api.search_idir_users(search_params)

            # Assert POST was called
            mock_post.assert_called_once()

            # Get the call arguments
            call_args = mock_post.call_args
            url = call_args[0][0]
            json_body = call_args[1]["json"]
            params = call_args[1]["params"]
            timeout = call_args[1]["timeout"]

            # Verify URL ends with /idir-users/search
            assert url.endswith("/idir-users/search")

            # Verify request body includes requesterUserGuid
            assert json_body == {"requesterUserGuid": self.requester.user_guid}

            # Verify query params include provided filters
            assert params["firstName"] == "John"
            assert params["lastName"] == "Doe"
            assert params["firstNameMatchMode"] == "Contains"
            assert params["pageSize"] == 25

            # Verify timeout is correct
            assert timeout == IdimProxyService.TIMEOUT

    def test_search_idir_users_raises_http_error_on_401(self):
        """Test that HTTP 401 errors bubble up."""
        idim_proxy_api = IdimProxyService(self.requester)
        search_params = IdimProxyIdirUsersSearchParamReqSchema(firstName="John")

        with patch.object(idim_proxy_api.session, "post") as mock_post:
            mock_post.return_value.raise_for_status.side_effect = HTTPError("401 Client Error")

            with pytest.raises(HTTPError) as excinfo:
                idim_proxy_api.search_idir_users(search_params)

            assert "401 Client Error" in str(excinfo.value)

    def test_search_idir_users_raises_http_error_on_400(self):
        """Test that HTTP 400 errors bubble up."""
        idim_proxy_api = IdimProxyService(self.requester)
        search_params = IdimProxyIdirUsersSearchParamReqSchema(firstName="John")

        with patch.object(idim_proxy_api.session, "post") as mock_post:
            mock_post.return_value.raise_for_status.side_effect = HTTPError("400 Bad Request")

            with pytest.raises(HTTPError) as excinfo:
                idim_proxy_api.search_idir_users(search_params)

            assert "400 Bad Request" in str(excinfo.value)

    def test_search_idir_users_supports_201_success_status(self):
        """Test that HTTP 201 Created status is handled as success."""
        idim_proxy_api = IdimProxyService(self.requester)
        search_params = IdimProxyIdirUsersSearchParamReqSchema(firstName="John")

        mock_response = {
            "totalItems": 1,
            "pageSize": 50,
            "items": [
                {
                    "userId": "john.doe",
                    "guid": "12345678123412341234123456789012",
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@gov.bc.ca",
                },
            ],
        }

        with patch.object(idim_proxy_api.session, "post") as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            result = idim_proxy_api.search_idir_users(search_params)

            assert result["totalItems"] == 1
            assert len(result["items"]) == 1

    def test_search_idir_users_logs_elapsed_time(self, caplog):
        """Test that elapsed time is logged for successful calls."""
        idim_proxy_api = IdimProxyService(self.requester)
        search_params = IdimProxyIdirUsersSearchParamReqSchema(firstName="John")

        mock_response = {
            "totalItems": 0,
            "pageSize": 50,
            "items": [],
        }

        with caplog.at_level(logging.INFO):
            with patch.object(idim_proxy_api.session, "post") as mock_post:
                mock_post.return_value.json.return_value = mock_response
                mock_post.return_value.raise_for_status.return_value = None

                idim_proxy_api.search_idir_users(search_params)

        # Check that timing log was emitted
        timing_logs = [record for record in caplog.records if "completed in" in record.message and "ms" in record.message]
        assert len(timing_logs) > 0
        assert "search_idir_users" in timing_logs[0].message

    def test_search_idir_users_logs_time_on_http_error(self, caplog):
        """Test that elapsed time is logged even on HTTP errors."""
        idim_proxy_api = IdimProxyService(self.requester)
        search_params = IdimProxyIdirUsersSearchParamReqSchema(firstName="John")

        with caplog.at_level(logging.INFO):
            with patch.object(idim_proxy_api.session, "post") as mock_post:
                mock_post.return_value.raise_for_status.side_effect = HTTPError("400 Bad Request")

                try:
                    idim_proxy_api.search_idir_users(search_params)
                except HTTPError:
                    pass

        # Check that timing log was emitted even though an error occurred
        timing_logs = [record for record in caplog.records if "completed in" in record.message and "ms" in record.message]
        assert len(timing_logs) > 0
        assert "search_idir_users" in timing_logs[0].message


# ============================================================================
# Schema validation tests
# ============================================================================
class TestIdimProxyIdirUsersSearchSchemas:
    """
    Testing schema validation for IDIM proxy IDIR users search.
    """

    def test_search_param_schema_missing_all_search_fields_fails_validation(self):
        """Test that at least one search field is required."""
        with pytest.raises(ValueError) as excinfo:
            IdimProxyIdirUsersSearchParamReqSchema()

        assert "At least one of firstName, lastName, or userId must be provided" in str(excinfo.value)

    def test_search_param_schema_with_firstname_passes_validation(self):
        """Test that providing firstName passes validation."""
        schema = IdimProxyIdirUsersSearchParamReqSchema(firstName="John")
        assert schema.firstName == "John"
        assert schema.pageSize == 50  # default

    def test_search_param_schema_with_lastname_passes_validation(self):
        """Test that providing lastName passes validation."""
        schema = IdimProxyIdirUsersSearchParamReqSchema(lastName="Doe")
        assert schema.lastName == "Doe"

    def test_search_param_schema_with_userid_passes_validation(self):
        """Test that providing userId passes validation."""
        schema = IdimProxyIdirUsersSearchParamReqSchema(userId="john.doe")
        assert schema.userId == "john.doe"

    def test_search_param_schema_invalid_pagesize_too_small_fails(self):
        """Test that pageSize below minimum fails validation."""
        with pytest.raises(ValueError):
            IdimProxyIdirUsersSearchParamReqSchema(
                firstName="John",
                pageSize=0,  # Below minimum
            )

    def test_search_param_schema_invalid_pagesize_too_large_fails(self):
        """Test that pageSize above maximum fails validation."""
        with pytest.raises(ValueError):
            IdimProxyIdirUsersSearchParamReqSchema(
                firstName="John",
                pageSize=1001,  # Above maximum
            )

    def test_search_param_schema_invalid_match_mode_fails(self):
        """Test that invalid match mode fails validation."""
        with pytest.raises(ValueError):
            IdimProxyIdirUsersSearchParamReqSchema(
                firstName="John",
                firstNameMatchMode="InvalidMode",  # Invalid enum value
            )

    def test_search_param_schema_valid_match_modes(self):
        """Test that all valid match modes are accepted."""
        schema1 = IdimProxyIdirUsersSearchParamReqSchema(
            firstName="John",
            firstNameMatchMode=IdimSearchMatchMode.EXACT,
        )
        assert schema1.firstNameMatchMode == IdimSearchMatchMode.EXACT

        schema2 = IdimProxyIdirUsersSearchParamReqSchema(
            firstName="John",
            firstNameMatchMode=IdimSearchMatchMode.CONTAINS,
        )
        assert schema2.firstNameMatchMode == IdimSearchMatchMode.CONTAINS

        schema3 = IdimProxyIdirUsersSearchParamReqSchema(
            firstName="John",
            firstNameMatchMode=IdimSearchMatchMode.STARTS_WITH,
        )
        assert schema3.firstNameMatchMode == IdimSearchMatchMode.STARTS_WITH

    def test_response_schema_parse_empty_items(self):
        """Test that response schema parses empty items list."""
        response_data = {
            "totalItems": 0,
            "pageSize": 50,
            "items": [],
        }
        schema = IdimProxyIdirUsersSearchResSchema(**response_data)
        assert schema.totalItems == 0
        assert schema.pageSize == 50
        assert len(schema.items) == 0

    def test_response_schema_parse_populated_items(self):
        """Test that response schema parses populated items."""
        response_data = {
            "totalItems": 2,
            "pageSize": 50,
            "items": [
                {
                    "userId": "john.doe",
                    "guid": "12345678123412341234123456789012",
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@gov.bc.ca",
                },
                {
                    "userId": "jane.smith",
                    "guid": "87654321432143214321210987654321",
                    "firstName": "Jane",
                    "lastName": "Smith",
                    "email": "jane.smith@gov.bc.ca",
                },
            ],
        }
        schema = IdimProxyIdirUsersSearchResSchema(**response_data)
        assert schema.totalItems == 2
        assert schema.pageSize == 50
        assert len(schema.items) == 2
        assert schema.items[0].userId == "john.doe"
        assert schema.items[1].userId == "jane.smith"

    def test_response_item_schema_single_item(self):
        """Test that response item schema validates correctly."""
        item_data = {
            "userId": "john.doe",
            "guid": "12345678123412341234123456789012",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@gov.bc.ca",
        }
        schema = IdimProxyIdirUserSearchItemResSchema(**item_data)
        assert schema.userId == "john.doe"
        assert schema.firstName == "John"
        assert schema.lastName == "Doe"
        assert schema.email == "john.doe@gov.bc.ca"

    def test_search_match_mode_enum_values(self):
        """Test that match mode enum has expected values."""
        assert IdimSearchMatchMode.EXACT.value == "Exact"
        assert IdimSearchMatchMode.CONTAINS.value == "Contains"
        assert IdimSearchMatchMode.STARTS_WITH.value == "StartsWith"
