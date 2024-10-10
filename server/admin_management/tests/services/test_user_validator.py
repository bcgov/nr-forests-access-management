import logging

import pytest
from api.app.constants import (ERROR_CODE_INVALID_REQUEST_PARAMETER,
                               ApiInstanceEnv, UserType)
from api.app.integration.idim_proxy import IdimProxyService
from api.app.schemas.schemas import Requester, TargetUser
from api.app.services.validator.target_user_validator import \
    TargetUserValidator
from fastapi import HTTPException
from mock import patch
from tests.constants import (TEST_USER_BUSINESS_GUID_BCEID,
                             TEST_USER_GUID_BCEID, TEST_USER_GUID_IDIR,
                             TEST_USER_NAME_BCEID, TEST_USER_NAME_IDIR)

LOGGER = logging.getLogger(__name__)


TEST_NEW_TARGET_USER_IDIR = {
    "user_type_code": UserType.IDIR,
    "user_name": TEST_USER_NAME_IDIR,
    "user_guid": TEST_USER_GUID_IDIR,
}

TEST_NEW_TARGET_USER_BCEID_LOAD_2 = {
    "user_type_code": UserType.BCEID,
    "user_name": TEST_USER_NAME_BCEID,
    "user_guid": TEST_USER_GUID_BCEID,
}

TEST_REQUESTER = {
    "user_id": 11,  # this is a faked id
    "user_type_code": UserType.IDIR,
    "user_name": TEST_USER_NAME_IDIR,
    "user_guid": TEST_USER_GUID_IDIR,
}

MOCK_SERACH_IDIR_RETURN = {
    "found": True,
    "guid": TEST_NEW_TARGET_USER_IDIR.get("user_guid"),
    "userId": TEST_NEW_TARGET_USER_IDIR.get("user_name"),
}

MOCK_SERACH_BCEID_RETURN = {
    "found": True,
    "guid": TEST_NEW_TARGET_USER_BCEID_LOAD_2.get("user_guid"),
    "userId": TEST_NEW_TARGET_USER_BCEID_LOAD_2.get("user_name"),
    "businessGuid": TEST_USER_BUSINESS_GUID_BCEID,
}


class TestUserValidatorClass(object):
    """
    Testing UserValidator class with mocked IDIM API calls.
    """

    def setup_class(self):
        # local valid mock requester
        self.requester_idir = Requester(**TEST_REQUESTER)

    @patch.object(IdimProxyService, "search_idir")
    def test_verify_user_exist_idir(self, mock_search_idir):
        mock_search_idir.return_value = MOCK_SERACH_IDIR_RETURN
        target_user = TargetUser(**TEST_NEW_TARGET_USER_IDIR)
        target_user_validaor = TargetUserValidator(self.requester_idir, target_user, ApiInstanceEnv.TEST)
        verified_target_user = target_user_validaor.verify_user_exist()

        # test the verified target user
        assert verified_target_user.user_guid == target_user.user_guid
        assert verified_target_user.user_type_code == target_user.user_type_code
        assert verified_target_user.user_name == target_user.user_name

    @patch.object(IdimProxyService, "search_idir")
    def test_verify_user_exist_idir_not_found(self, mock_search_idir):
        mock_search_idir.return_value = {**MOCK_SERACH_IDIR_RETURN, "found": False}
        target_user = TargetUser(
            **{**TEST_NEW_TARGET_USER_IDIR, "user_name": "USER_NOT_EXISTS"}
        )
        target_user_validaor = TargetUserValidator(self.requester_idir, target_user, ApiInstanceEnv.TEST)

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
        target_user = TargetUser(
            **{
                **TEST_NEW_TARGET_USER_IDIR,
                "user_guid": "USERGUIDNOTEXISTSPOJHSLEJFNSEKSL",
            }
        )
        target_user_validaor = TargetUserValidator(self.requester_idir, target_user, ApiInstanceEnv.TEST)

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
        target_user = TargetUser(**TEST_NEW_TARGET_USER_BCEID_LOAD_2)
        target_user_validaor = TargetUserValidator(self.requester_idir, target_user, ApiInstanceEnv.TEST)
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
        target_user = TargetUser(
            **{
                **TEST_NEW_TARGET_USER_BCEID_LOAD_2,
                "user_guid": "USERGUIDNOTEXISTSPOJHSLEJFNSEKSL",
            }
        )
        target_user_validaor = TargetUserValidator(self.requester_idir, target_user, ApiInstanceEnv.TEST)

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
        target_user = TargetUser(
            **{
                **TEST_NEW_TARGET_USER_BCEID_LOAD_2,
                "user_name": "USER_NOT_EXISTS",
            }
        )
        target_user_validaor = TargetUserValidator(self.requester_idir, target_user, ApiInstanceEnv.TEST)

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
