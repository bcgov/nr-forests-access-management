import os
import logging
import pytest
from fastapi import HTTPException

from api.app.crud.validator.user_validator import UserValidator
from api.app.schemas import Requester, TargetUser
from api.app.constants import ERROR_CODE_INVALID_REQUEST_PARAMETER, UserType
from testspg.constants import TEST_IDIR_REQUESTER_DICT, USER_NAME_BCEID_LOAD_2_TEST, USER_GUID_BCEID_LOAD_2_TEST


LOGGER = logging.getLogger(__name__)

# when run test locally, we can use our own idir username and user guid
TEST_IDIR_USER_GUID = os.environ.get("TEST_IDIR_USER_GUID")
TEST_IDIR_USER_NAME = os.environ.get(
    "TEST_IDIR_USER_NAME"
) or TEST_IDIR_REQUESTER_DICT.get("user_name")

TEST_USER_IDIR = {
    **TEST_IDIR_REQUESTER_DICT,
    "user_name": TEST_IDIR_USER_NAME,
    "user_guid": TEST_IDIR_USER_GUID,
}

TEST_TARGET_USER_BCEID_LOAD_2 = {
    "user_type_code": UserType.BCEID,
    "user_name": USER_NAME_BCEID_LOAD_2_TEST,
    "user_guid": USER_GUID_BCEID_LOAD_2_TEST,
}


class TestUserValidatorClass(object):
    """
    Testing UserValidator class with real remote API calls (TEST environment).
    """

    def setup_class(self):
        # local valid mock requester
        self.requester_idir = Requester(**TEST_USER_IDIR)

    def test_verify_user_exist_idir(self):
        target_user = TargetUser(**TEST_USER_IDIR)
        user_validaor = UserValidator(self.requester_idir, target_user)
        verified_target_user = user_validaor.verify_user_exist()
        # test the verified target user
        assert verified_target_user.user_guid == target_user.user_guid
        assert verified_target_user.user_type_code == target_user.user_type_code
        assert verified_target_user.user_name == target_user.user_name

    def test_verify_user_exist_idir_not_found(self):
        target_user = TargetUser(**{**TEST_USER_IDIR, "user_name": "USER_NOT_EXISTS"})
        user_validaor = UserValidator(self.requester_idir, target_user)

        with pytest.raises(HTTPException) as e:
            user_validaor.verify_user_exist()
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

    def test_verify_user_exist_idir_mismatch_info(self):
        target_user = TargetUser(
            **{
                **TEST_USER_IDIR,
                "user_guid": "USERGUIDNOTEXISTSPOJHSLEJFNSEKSL",
            }
        )
        user_validaor = UserValidator(self.requester_idir, target_user)

        with pytest.raises(HTTPException) as e:
            user_validaor.verify_user_exist()
        assert (
            str(e.value.detail.get("code")).find(ERROR_CODE_INVALID_REQUEST_PARAMETER)
            != -1
        )
        assert (
            str(e.value.detail.get("description")).find("does not match the user guid")
            != -1
        )

    def test_verify_user_exist_bceid(self):
        target_user = TargetUser(**TEST_TARGET_USER_BCEID_LOAD_2)
        user_validaor = UserValidator(self.requester_idir, target_user)
        verified_target_user = user_validaor.verify_user_exist()
        # test the verified target user, business guid is added
        assert verified_target_user.user_guid == target_user.user_guid
        assert verified_target_user.user_type_code == target_user.user_type_code
        assert verified_target_user.user_name == target_user.user_name
        assert verified_target_user.business_guid is not None

    # def test_verify_user_exist_bceid_not_found(self):
    #     target_user = TargetUser(
    #         **{
    #             **TEST_TARGET_USER_BCEID_LOAD_2,
    #             "user_guid": "USERGUIDNOTEXISTSPOJHSLEJFNSEKSL",
    #         }
    #     )
    #     user_validaor = UserValidator(self.requester_idir, target_user)

    #     with pytest.raises(HTTPException) as e:
    #         user_validaor.verify_user_exist()
    #     assert (
    #         str(e.value.detail.get("code")).find(ERROR_CODE_INVALID_REQUEST_PARAMETER)
    #         != -1
    #     )
    #     assert (
    #         str(e.value.detail.get("description")).find(
    #             "Invalid request, cannot find user"
    #         )
    #         != -1
    #     )

    # def test_verify_user_exist_bceid_mismatch_info(self):
    #     target_user = TargetUser(
    #         **{
    #             **TEST_TARGET_USER_BCEID_LOAD_2,
    #             "user_name": "USER_NOT_EXISTS",
    #         }
    #     )
    #     user_validaor = UserValidator(self.requester_idir, target_user)

    #     with pytest.raises(HTTPException) as e:
    #         user_validaor.verify_user_exist()
    #     assert (
    #         str(e.value.detail.get("code")).find(ERROR_CODE_INVALID_REQUEST_PARAMETER)
    #         != -1
    #     )
    #     assert (
    #         str(e.value.detail.get("description")).find("does not match the username")
    #         != -1
    #     )
