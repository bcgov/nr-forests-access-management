import logging

import pytest
from api.app.constants import (
    ERROR_CODE_INVALID_REQUEST_PARAMETER,
    UserType,
    ApiInstanceEnv,
)
from api.app.crud.validator.target_user_validator import TargetUserValidator
from api.app.integration.idim_proxy import IdimProxyService
from api.app.schemas import RequesterSchema, TargetUserSchema
from fastapi import HTTPException
from mock import patch
from testspg.constants import (
    BUSINESS_GUID_BCEID_LOAD_2_TEST,
    TEST_IDIR_REQUESTER_DICT,
    USER_GUID_BCEID_LOAD_2_TEST,
    USER_NAME_BCEID_LOAD_2_TEST,
)

LOGGER = logging.getLogger(__name__)


TEST_TARGET_USER_BCEID_LOAD_2 = {
    "user_type_code": UserType.BCEID,
    "user_name": USER_NAME_BCEID_LOAD_2_TEST,
    "user_guid": USER_GUID_BCEID_LOAD_2_TEST,
}

MOCK_SERACH_IDIR_RETURN = {
    "found": True,
    "guid": TEST_IDIR_REQUESTER_DICT.get("user_guid"),
    "userId": TEST_IDIR_REQUESTER_DICT.get("user_name"),
}

MOCK_SERACH_BCEID_RETURN = {
    "found": True,
    "guid": TEST_TARGET_USER_BCEID_LOAD_2.get("user_guid"),
    "userId": TEST_TARGET_USER_BCEID_LOAD_2.get("user_name"),
    "businessGuid": BUSINESS_GUID_BCEID_LOAD_2_TEST,
}


class TestUserValidatorClass(object):
    """
    Testing UserValidator class with mocked IDIM API calls.
    """

    def setup_class(self):
        # local valid mock RequesterSchema
        self.requester_idir = RequesterSchema(**TEST_IDIR_REQUESTER_DICT)

    @patch.object(IdimProxyService, "search_idir")
    def test_verify_user_exist_idir(self, mock_search_idir):
        mock_search_idir.return_value = MOCK_SERACH_IDIR_RETURN
        target_user = TargetUserSchema(**TEST_IDIR_REQUESTER_DICT)
        target_user_validaor = TargetUserValidator(
            self.requester_idir, target_user, ApiInstanceEnv.TEST
        )
        verified_target_user = target_user_validaor.verify_user_exist()
        # test the verified target user
        assert verified_target_user.user_guid == target_user.user_guid
        assert verified_target_user.user_type_code == target_user.user_type_code
        assert verified_target_user.user_name == target_user.user_name

    @patch.object(IdimProxyService, "search_idir")
    def test_verify_user_exist_idir_not_found(self, mock_search_idir):
        mock_search_idir.return_value = {**MOCK_SERACH_IDIR_RETURN, "found": False}
        target_user = TargetUserSchema(
            **{**TEST_IDIR_REQUESTER_DICT, "user_name": "USER_NOT_EXISTS"}
        )
        target_user_validaor = TargetUserValidator(
            self.requester_idir, target_user, ApiInstanceEnv.TEST
        )

        with pytest.raises(HTTPException) as e:
            target_user_validaor.verify_user_exist()
        assert (
            str(e.value.detail.get("code")).find(ERROR_CODE_INVALID_REQUEST_PARAMETER)
            != -1
        )
        assert (
            str(e.value.detail.get("description")).find(
                "Invalid request, cannot find user"
            )
            != -1
        )

    @patch.object(IdimProxyService, "search_idir")
    def test_verify_user_exist_idir_mismatch_info(self, mock_search_idir):
        mock_search_idir.return_value = MOCK_SERACH_IDIR_RETURN
        target_user = TargetUserSchema(
            **{
                **TEST_IDIR_REQUESTER_DICT,
                "user_guid": "USERGUIDNOTEXISTSPOJHSLEJFNSEKSL",
            }
        )
        target_user_validaor = TargetUserValidator(
            self.requester_idir, target_user, ApiInstanceEnv.TEST
        )

        with pytest.raises(HTTPException) as e:
            target_user_validaor.verify_user_exist()
        assert (
            str(e.value.detail.get("code")).find(ERROR_CODE_INVALID_REQUEST_PARAMETER)
            != -1
        )
        assert (
            str(e.value.detail.get("description")).find("does not match the user guid")
            != -1
        )

    @patch.object(IdimProxyService, "search_business_bceid")
    def test_verify_user_exist_bceid(self, mock_search_business_bceid):
        mock_search_business_bceid.return_value = MOCK_SERACH_BCEID_RETURN
        target_user = TargetUserSchema(**TEST_TARGET_USER_BCEID_LOAD_2)
        target_user_validaor = TargetUserValidator(
            self.requester_idir, target_user, ApiInstanceEnv.TEST
        )
        verified_target_user = target_user_validaor.verify_user_exist()
        # test the verified target user, business guid is added
        assert verified_target_user.user_guid == target_user.user_guid
        assert verified_target_user.user_type_code == target_user.user_type_code
        assert verified_target_user.user_name == target_user.user_name
        assert verified_target_user.business_guid is not None

    @patch.object(IdimProxyService, "search_business_bceid")
    def test_verify_user_exist_bceid_not_found(self, mock_search_business_bceid):
        mock_search_business_bceid.return_value = {
            **MOCK_SERACH_BCEID_RETURN,
            "found": False,
        }
        target_user = TargetUserSchema(
            **{
                **TEST_TARGET_USER_BCEID_LOAD_2,
                "user_guid": "USERGUIDNOTEXISTSPOJHSLEJFNSEKSL",
            }
        )
        target_user_validaor = TargetUserValidator(
            self.requester_idir, target_user, ApiInstanceEnv.TEST
        )

        with pytest.raises(HTTPException) as e:
            target_user_validaor.verify_user_exist()
        assert (
            str(e.value.detail.get("code")).find(ERROR_CODE_INVALID_REQUEST_PARAMETER)
            != -1
        )
        assert (
            str(e.value.detail.get("description")).find(
                "Invalid request, cannot find user"
            )
            != -1
        )

    @patch.object(IdimProxyService, "search_business_bceid")
    def test_verify_user_exist_bceid_mismatch_info(self, mock_search_business_bceid):
        mock_search_business_bceid.return_value = MOCK_SERACH_BCEID_RETURN
        target_user = TargetUserSchema(
            **{
                **TEST_TARGET_USER_BCEID_LOAD_2,
                "user_name": "USER_NOT_EXISTS",
            }
        )
        target_user_validaor = TargetUserValidator(
            self.requester_idir, target_user, ApiInstanceEnv.TEST
        )

        with pytest.raises(HTTPException) as e:
            target_user_validaor.verify_user_exist()
        assert (
            str(e.value.detail.get("code")).find(ERROR_CODE_INVALID_REQUEST_PARAMETER)
            != -1
        )
        assert (
            str(e.value.detail.get("description")).find("does not match the username")
            != -1
        )
