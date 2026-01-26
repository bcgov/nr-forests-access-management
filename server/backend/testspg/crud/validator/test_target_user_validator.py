import logging
import pytest
from api.app.constants import (
    ERROR_CODE_INVALID_REQUEST_PARAMETER,
    UserType,
    ApiInstanceEnv,
)
from api.app.crud.validator.target_user_validator import TargetUserValidator, validate_bceid_same_org, validate_target_users
from api.app.integration.idim_proxy import IdimProxyService
from api.app.schemas import RequesterSchema, TargetUserSchema
from fastapi import HTTPException
from mock import patch
from api.app.schemas.target_user_validation_result import FailedTargetUserSchema, TargetUserValidationResultSchema
from testspg.crud.test_crud_user_role import TEST_USER_ID
from testspg.constants import (
    BUSINESS_GUID_BCEID_LOAD_2_TEST, TEST_BCEID_REQUESTER_DICT, TEST_IDIR_REQUESTER_DICT, TEST_USER_GUID_IDIR, USER_GUID_BCEID_LOAD_2_TEST, USER_GUID_BCEID_LOAD_3_TEST, USER_GUID_BCEID_LOAD_4_TEST, USER_NAME_BCEID_LOAD_2_TEST
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

# --- tests for validate_target_users ---

class DummyFamRole:
    """Minimal dummy FamRole for testing."""
    def __init__(self, application):
        self.application = application

@patch.object(IdimProxyService, "search_idir")
def test_validate_target_users_all_verified(mock_search_idir):
    """
    Test validate_target_users where all users are valid and verified.
    """
    mock_search_idir.return_value = MOCK_SERACH_IDIR_RETURN
    requester = RequesterSchema(**TEST_IDIR_REQUESTER_DICT)
    target_users = [TargetUserSchema(**TEST_IDIR_REQUESTER_DICT)]
    fam_role = DummyFamRole(application="FOM")
    result = validate_target_users(requester, target_users, fam_role)
    assert isinstance(result, TargetUserValidationResultSchema)
    assert len(result.verified_users) == 1
    assert len(result.failed_users) == 0
    assert result.verified_users[0].user_guid == target_users[0].user_guid


@patch.object(IdimProxyService, "search_idir")
def test_validate_target_users_some_failed(mock_search_idir):
    """
    Test validate_target_users where some users fail validation.
    """
    # First user found, second user not found
    def side_effect(param):
        if param.userId == TEST_IDIR_REQUESTER_DICT["user_name"]:
            return MOCK_SERACH_IDIR_RETURN
        return {**MOCK_SERACH_IDIR_RETURN, "found": False}
    mock_search_idir.side_effect = side_effect

    requester = RequesterSchema(**TEST_IDIR_REQUESTER_DICT)
    valid_user = TargetUserSchema(**TEST_IDIR_REQUESTER_DICT)
    invalid_user_dict = {**TEST_IDIR_REQUESTER_DICT, "user_name": "USER_NOT_EXISTS", "user_guid": "GUID_NOT_EXISTS_1234567890123456"}
    invalid_user = TargetUserSchema(**invalid_user_dict)
    fam_role = DummyFamRole(application="FOM")

    result = validate_target_users(requester, [valid_user, invalid_user], fam_role)
    assert isinstance(result, TargetUserValidationResultSchema)
    assert len(result.verified_users) == 1
    assert len(result.failed_users) == 1
    assert result.verified_users[0].user_guid == valid_user.user_guid
    failed = result.failed_users[0]
    assert isinstance(failed, FailedTargetUserSchema)
    assert failed.user_name == invalid_user.user_name
    assert failed.user_guid == invalid_user.user_guid
    assert "cannot find user" in failed.error_reason


@patch.object(IdimProxyService, "search_idir")
def test_validate_target_users_all_failed(mock_search_idir):
    """
    Test validate_target_users where all users fail validation.
    """
    mock_search_idir.return_value = {**MOCK_SERACH_IDIR_RETURN, "found": False}

    requester = RequesterSchema(**TEST_IDIR_REQUESTER_DICT)
    user1 = TargetUserSchema(**{**TEST_IDIR_REQUESTER_DICT, "user_name": "USER_NOT_EXISTS1", "user_guid": "BADUSERGUID000000000000000000001"})
    user2 = TargetUserSchema(**{**TEST_IDIR_REQUESTER_DICT, "user_name": "USER_NOT_EXISTS2", "user_guid": "BADUSERGUID000000000000000000002"})
    fam_role = DummyFamRole(application="FOM")
    result = validate_target_users(requester, [user1, user2], fam_role)
    assert isinstance(result, TargetUserValidationResultSchema)
    assert len(result.verified_users) == 0
    assert len(result.failed_users) == 2
    for failed in result.failed_users:
        assert isinstance(failed, FailedTargetUserSchema)
        assert "cannot find user" in failed.error_reason


@patch.object(IdimProxyService, "search_business_bceid")
def test_validate_target_users_on_bceid_user(mock_search_business_bceid):
    """
    validate_target_users with a valid BCeID user.
    """
    mock_search_business_bceid.return_value = MOCK_SERACH_BCEID_RETURN
    requester = RequesterSchema(**TEST_BCEID_REQUESTER_DICT)
    target_users = [TargetUserSchema(**TEST_TARGET_USER_BCEID_LOAD_2)]
    fam_role = DummyFamRole(application="FOM")
    result = validate_target_users(requester, target_users, fam_role)
    assert isinstance(result, TargetUserValidationResultSchema)
    assert len(result.verified_users) == 1
    assert len(result.failed_users) == 0
    verified = result.verified_users[0]
    assert verified.user_guid == target_users[0].user_guid
    assert verified.user_type_code == target_users[0].user_type_code
    assert verified.user_name == target_users[0].user_name
    assert verified.business_guid == BUSINESS_GUID_BCEID_LOAD_2_TEST


# --- tests for validate_bceid_same_org
def test_validate_bceid_same_org_success():
    requester = RequesterSchema(
        user_name="requester_user",
        user_type_code=UserType.BCEID,
        business_guid="ORG123",
        user_guid=USER_GUID_BCEID_LOAD_4_TEST,
        user_id=TEST_USER_ID
    )
    target_users = [
        TargetUserSchema(user_name="target_user_1", business_guid="ORG123", user_guid=USER_GUID_BCEID_LOAD_2_TEST),
        TargetUserSchema(user_name="target_user_2", business_guid="ORG123", user_guid=USER_GUID_BCEID_LOAD_3_TEST)
    ]

    # Should not raise any exception
    validate_bceid_same_org(requester, target_users)


def test_bceid_requester_cannot_manage_different_org_user():
    """
    Ensure that a BCeID requester cannot manage a target user from a different organization.
    Should raise ValueError if orgs do not match.
    """
    requester = RequesterSchema(
        user_name="requester_user",
        user_type_code=UserType.BCEID,
        business_guid="ORG123",
        user_guid=USER_GUID_BCEID_LOAD_4_TEST,
        user_id=TEST_USER_ID
    )
    target_users = [
        TargetUserSchema(user_name="target_user_1", business_guid="ORG456", user_guid=USER_GUID_BCEID_LOAD_2_TEST)
    ]

    with pytest.raises(ValueError, match="Managing user target_user_1 from a different organization is not allowed."):
        validate_bceid_same_org(requester, target_users)


def test_validate_bceid_same_org_missing_requester_business_guid():
    requester = RequesterSchema(
        user_name="requester_user",
        user_type_code=UserType.BCEID,
        business_guid=None,
        user_guid=USER_GUID_BCEID_LOAD_4_TEST,
        user_id=TEST_USER_ID
    )
    target_users = [
        TargetUserSchema(user_name="target_user_1", business_guid="ORG123", user_guid=USER_GUID_BCEID_LOAD_2_TEST)
    ]

    with pytest.raises(ValueError, match="Requester or target user business GUID is missing."):
        validate_bceid_same_org(requester, target_users)


def test_validate_bceid_same_org_missing_target_user_business_guid():
    requester = RequesterSchema(
        user_name="requester_user",
        user_type_code=UserType.BCEID,
        business_guid="ORG123",
        user_guid=USER_GUID_BCEID_LOAD_4_TEST,
        user_id=TEST_USER_ID
    )
    target_users = [
        TargetUserSchema(user_name="target_user_1", business_guid=None, user_guid=USER_GUID_BCEID_LOAD_2_TEST)
    ]

    with pytest.raises(ValueError, match="Requester or target user business GUID is missing."):
        validate_bceid_same_org(requester, target_users)


def test_validate_bceid_same_org_idir_requester():
    requester = RequesterSchema(
        user_name="requester_user",
        user_type_code=UserType.IDIR,
        business_guid=None,
        user_guid=TEST_USER_GUID_IDIR,
        user_id=TEST_USER_ID
    )
    target_users = [
        TargetUserSchema(user_name="target_user_1", business_guid="ORG456", user_guid=USER_GUID_BCEID_LOAD_2_TEST)
    ]

    # Should not raise any exception since the requester is IDIR
    validate_bceid_same_org(requester, target_users)