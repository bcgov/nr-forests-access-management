import logging
import pytest
from sqlalchemy.exc import IntegrityError

from api.app.schemas import FamAccessControlPrivilegeCreateDto
from api.app.repositories.access_control_privilege_repository import (
    AccessControlPrivilegeRepository,
)
from tests.constants import (
    TEST_NON_EXIST_ACCESS_CONTROL_PRIVILEGE_ID,
    TEST_ACCESS_CONTROL_PRIVILEGE_CREATE,
    TEST_NON_EXIST_USER_ID,
    TEST_USER_ID,
    TEST_NOT_EXIST_ROLE_ID,
    TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    ERROR_VOLIATE_UNIQUE_CONSTRAINT,
    ERROR_VOLIATE_FOREIGN_KEY_CONSTRAINT,
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
