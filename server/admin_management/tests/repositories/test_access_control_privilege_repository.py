import logging

import pytest
from api.app.repositories.access_control_privilege_repository import (
    AccessControlPrivilegeRepository,
)
from api.app.repositories.user_repository import UserRepository
from api.app.schemas import FamAccessControlPrivilegeCreateDto
from sqlalchemy.exc import IntegrityError
from tests.constants import (
    ERROR_VOLIATE_FOREIGN_KEY_CONSTRAINT,
    ERROR_VOLIATE_UNIQUE_CONSTRAINT,
    TEST_ACCESS_CONTROL_PRIVILEGE_CREATE,
    TEST_APPLICATION_ID_FOM_DEV,
    TEST_CREATOR,
    TEST_FOM_DEV_REVIEWER_ROLE_ID,
    TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    TEST_FOM_TEST_REVIEWER_ROLE_ID,
    TEST_NEW_IDIR_USER,
    TEST_NON_EXIST_ACCESS_CONTROL_PRIVILEGE_ID,
    TEST_NON_EXIST_USER_ID,
    TEST_NOT_EXIST_APPLICATION_ID,
    TEST_NOT_EXIST_ROLE_ID,
    TEST_USER_ID,
)

LOGGER = logging.getLogger(__name__)


def test_get_acp_by_id(access_control_privilege_repo: AccessControlPrivilegeRepository):
    # get non exist access control privilege id
    found_record = access_control_privilege_repo.get_acp_by_id(
        TEST_NON_EXIST_ACCESS_CONTROL_PRIVILEGE_ID
    )
    assert found_record is None

    # create a new access control privilege
    new_record = access_control_privilege_repo.create_access_control_privilege(
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE
    )
    assert new_record.user_id == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.user_id
    assert new_record.role_id == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.role_id
    # get the new created access control privilege
    found_record = access_control_privilege_repo.get_acp_by_id(
        new_record.access_control_privilege_id
    )
    assert (
        found_record.access_control_privilege_id
        == new_record.access_control_privilege_id
    )
    assert found_record.user_id == new_record.user_id
    assert found_record.role_id == new_record.role_id


def test_get_acp_by_user_id_and_role_id(
    access_control_privilege_repo: AccessControlPrivilegeRepository,
):
    # get with non exist user id
    found_record = access_control_privilege_repo.get_acp_by_user_id_and_role_id(
        TEST_NON_EXIST_USER_ID, TEST_FOM_DEV_SUBMITTER_ROLE_ID
    )
    assert found_record is None

    # get with non exist role id
    found_record = access_control_privilege_repo.get_acp_by_user_id_and_role_id(
        TEST_USER_ID, TEST_NOT_EXIST_ROLE_ID
    )
    assert found_record is None

    # create a new access control privilege
    new_record = access_control_privilege_repo.create_access_control_privilege(
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE
    )
    assert new_record.user_id == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.user_id
    assert new_record.role_id == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.role_id
    # get the new access control privilege by user id and role id
    found_record = access_control_privilege_repo.get_acp_by_user_id_and_role_id(
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.user_id,
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.role_id,
    )
    assert found_record.user_id == new_record.user_id
    assert found_record.role_id == new_record.role_id


def test_create_access_control_privilege(
    access_control_privilege_repo: AccessControlPrivilegeRepository,
):
    # create a new access control privilege
    new_record = access_control_privilege_repo.create_access_control_privilege(
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE
    )
    assert new_record.user_id == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.user_id
    assert new_record.role_id == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.role_id

    # create duplicate application admin
    with pytest.raises(IntegrityError) as e:
        access_control_privilege_repo.create_access_control_privilege(
            TEST_ACCESS_CONTROL_PRIVILEGE_CREATE
        )
    assert str(e.value).find(ERROR_VOLIATE_UNIQUE_CONSTRAINT) != -1


def test_create_access_control_privilege_invalid_user_id(
    access_control_privilege_repo: AccessControlPrivilegeRepository,
):
    # create with non exists user id
    test_data_dict = TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.model_dump()
    with pytest.raises(IntegrityError) as e:
        access_control_privilege_repo.create_access_control_privilege(
            FamAccessControlPrivilegeCreateDto(
                **{**test_data_dict, "user_id": TEST_NON_EXIST_USER_ID}
            )
        )
    assert str(e.value).find(ERROR_VOLIATE_FOREIGN_KEY_CONSTRAINT) != -1


def test_create_access_control_privilege_invalid_role_id(
    access_control_privilege_repo: AccessControlPrivilegeRepository,
):
    # create with non exists role id
    test_data_dict = TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.model_dump()
    with pytest.raises(IntegrityError) as e:
        access_control_privilege_repo.create_access_control_privilege(
            FamAccessControlPrivilegeCreateDto(
                **{**test_data_dict, "role_id": TEST_NOT_EXIST_ROLE_ID}
            )
        )
    assert str(e.value).find(ERROR_VOLIATE_FOREIGN_KEY_CONSTRAINT) != -1


def test_get_acp_by_application_id(
    access_control_privilege_repo: AccessControlPrivilegeRepository,
):
    init_records = access_control_privilege_repo.get_acp_by_application_id(
        TEST_APPLICATION_ID_FOM_DEV
    )
    # create a new access control privilege
    new_record = access_control_privilege_repo.create_access_control_privilege(
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE
    )
    assert new_record.user_id == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.user_id
    assert new_record.role_id == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.role_id
    # check the number of records increased
    current_records = access_control_privilege_repo.get_acp_by_application_id(
        TEST_APPLICATION_ID_FOM_DEV
    )
    assert len(current_records) == len(init_records) + 1

    # test get with non exist application id
    found_acp = access_control_privilege_repo.get_acp_by_application_id(
        TEST_NOT_EXIST_APPLICATION_ID
    )
    assert len(found_acp) == 0


def test_delete_access_control_privileg(
    access_control_privilege_repo: AccessControlPrivilegeRepository,
):
    # create a new access control privilege
    new_access_control_privilege = (
        access_control_privilege_repo.create_access_control_privilege(
            TEST_ACCESS_CONTROL_PRIVILEGE_CREATE
        )
    )
    assert (
        new_access_control_privilege.user_id
        == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.user_id
    )
    assert (
        new_access_control_privilege.role_id
        == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE.role_id
    )
    # verify the new access control privilege is created
    access_control_privilege = access_control_privilege_repo.get_acp_by_id(
        new_access_control_privilege.access_control_privilege_id
    )
    assert access_control_privilege is not None

    # remove the access control privilege
    access_control_privilege_repo.delete_access_control_privilege(
        new_access_control_privilege.access_control_privilege_id
    )
    # verify the access control privilege cannot be found anymore
    access_control_privilege = access_control_privilege_repo.get_acp_by_id(
        new_access_control_privilege.access_control_privilege_id
    )
    assert access_control_privilege is None


def test_get_user_delegated_admin_grants(
    access_control_privilege_repo: AccessControlPrivilegeRepository,
    user_repo: UserRepository,
):
    new_user = user_repo.create_user(TEST_NEW_IDIR_USER)

    # user does not have delegated admin privilege initially.
    initial_granted_role = (
        access_control_privilege_repo.get_user_delegated_admin_grants(new_user.user_id)
    )
    assert initial_granted_role == []

    # granted new user delegated admin a role
    fom_dev_reviewer_delegated_request = FamAccessControlPrivilegeCreateDto(
        **{
            "user_id": new_user.user_id,
            "role_id": TEST_FOM_DEV_REVIEWER_ROLE_ID,
            "create_user": TEST_CREATOR,
        }
    )
    access_control_privilege_repo.create_access_control_privilege(
        fom_dev_reviewer_delegated_request
    )

    user_grants = access_control_privilege_repo.get_user_delegated_admin_grants(
        new_user.user_id
    )
    assert len(user_grants) == 1
    granted_fom_reviewer_role = user_grants[0]
    assert granted_fom_reviewer_role.role_id == TEST_FOM_DEV_REVIEWER_ROLE_ID

    # granted new user delegated admin, mutilple roles
    fom_test_reviewer_delegated_request = FamAccessControlPrivilegeCreateDto(
        **{
            "user_id": new_user.user_id,
            "role_id": TEST_FOM_TEST_REVIEWER_ROLE_ID,
            "create_user": TEST_CREATOR,
        }
    )
    access_control_privilege_repo.create_access_control_privilege(
        fom_test_reviewer_delegated_request
    )
    user_grants = access_control_privilege_repo.get_user_delegated_admin_grants(
        new_user.user_id
    )
    assert len(user_grants) == 2
    granted_role_list = list(map(lambda x: x.role_id, user_grants))
    assert set(granted_role_list) == set(
        [TEST_FOM_DEV_REVIEWER_ROLE_ID, TEST_FOM_TEST_REVIEWER_ROLE_ID]
    )
