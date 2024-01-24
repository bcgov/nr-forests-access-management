import logging
import pytest
from sqlalchemy.exc import IntegrityError

from api.app import constants as famConstants
from api.app.repositories.role_repository import RoleRepository
from tests.constants import (
    TEST_NOT_EXIST_ROLE_ID,
    TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    TEST_FOM_DEV_REVIEWER_ROLE_ID,
    TEST_NOT_EXIST_APPLICATION_ID,
    TEST_APPLICATION_ID_FOM_DEV,
    TEST_APPLICATION_ID_FAM,
    TEST_NON_EXIST_ROLE_NAME,
    TEST_FOM_REVIEWER_ROLE_NAME,
    TEST_ROLE_CREATE_CONCRETE,
    TEST_ROLE_CREATE_ABSTRACT,
    TEST_ROLE_CREATE_CHILD,
    TEST_ANOTHER_CREATER,
    ERROR_VOLIATE_UNIQUE_CONSTRAINT,
    ERROR_VOLIATE_FOREIGN_KEY_CONSTRAINT,
)


LOGGER = logging.getLogger(__name__)


def test_get_role_by_id(role_repo: RoleRepository):
    # get non exists role
    found_role = role_repo.get_role_by_id(TEST_NOT_EXIST_ROLE_ID)
    assert found_role is None

    # get concreate role
    found_role = role_repo.get_role_by_id(TEST_FOM_DEV_REVIEWER_ROLE_ID)
    assert found_role.role_id == TEST_FOM_DEV_REVIEWER_ROLE_ID
    assert found_role.application_id == TEST_APPLICATION_ID_FOM_DEV
    assert found_role.role_type_code == famConstants.RoleType.ROLE_TYPE_CONCRETE

    # get abstract role
    found_role = role_repo.get_role_by_id(TEST_FOM_DEV_SUBMITTER_ROLE_ID)
    assert found_role.role_id == TEST_FOM_DEV_SUBMITTER_ROLE_ID
    assert found_role.application_id == TEST_APPLICATION_ID_FOM_DEV
    assert found_role.role_type_code == famConstants.RoleType.ROLE_TYPE_ABSTRACT


def test_get_role_by_role_name_and_app_id(role_repo: RoleRepository):
    # get with non existing role name
    found_role = role_repo.get_role_by_role_name_and_app_id(
        TEST_NON_EXIST_ROLE_NAME, TEST_APPLICATION_ID_FOM_DEV
    )
    assert found_role is None

    # get with non existing application id
    found_role = role_repo.get_role_by_role_name_and_app_id(
        TEST_FOM_REVIEWER_ROLE_NAME, TEST_NOT_EXIST_APPLICATION_ID
    )
    assert found_role is None

    # get with role not in application
    found_role = role_repo.get_role_by_role_name_and_app_id(
        TEST_FOM_REVIEWER_ROLE_NAME, TEST_APPLICATION_ID_FAM
    )
    assert found_role is None

    # get existing role
    found_role = role_repo.get_role_by_role_name_and_app_id(
        TEST_FOM_REVIEWER_ROLE_NAME, TEST_APPLICATION_ID_FOM_DEV
    )
    assert found_role.role_name == TEST_FOM_REVIEWER_ROLE_NAME


def test_create_role(role_repo: RoleRepository):
    # create concrete role
    new_concrete_role = role_repo.create_role(TEST_ROLE_CREATE_CONCRETE)
    assert new_concrete_role.role_name == TEST_ROLE_CREATE_CONCRETE.get("role_name")
    assert new_concrete_role.role_type_code == famConstants.RoleType.ROLE_TYPE_CONCRETE
    # verify concrete role created
    found_role = role_repo.get_role_by_id(new_concrete_role.role_id)
    assert found_role.role_id == new_concrete_role.role_id
    assert found_role.role_name == TEST_ROLE_CREATE_CONCRETE.get("role_name")
    assert found_role.application_id == TEST_ROLE_CREATE_CONCRETE.get("application_id")
    assert found_role.role_type_code == TEST_ROLE_CREATE_CONCRETE.get("role_type_code")

    # create abstract role
    new_abstract_role = role_repo.create_role(TEST_ROLE_CREATE_ABSTRACT)
    assert new_abstract_role.role_name == TEST_ROLE_CREATE_ABSTRACT.get("role_name")
    assert new_abstract_role.role_type_code == famConstants.RoleType.ROLE_TYPE_ABSTRACT
    # verify abstract role created
    found_role = role_repo.get_role_by_id(new_abstract_role.role_id)
    assert found_role.role_id == new_abstract_role.role_id
    assert found_role.role_name == TEST_ROLE_CREATE_ABSTRACT.get("role_name")
    assert found_role.application_id == TEST_ROLE_CREATE_ABSTRACT.get("application_id")
    assert found_role.role_type_code == TEST_ROLE_CREATE_ABSTRACT.get("role_type_code")

    # create same role name with different application
    second_concrete_role = role_repo.create_role(
        {**TEST_ROLE_CREATE_CONCRETE, "application_id": TEST_APPLICATION_ID_FAM}
    )
    # verify second role created
    found_role = role_repo.get_role_by_id(second_concrete_role.role_id)
    assert found_role.role_id == second_concrete_role.role_id
    assert found_role.role_name == TEST_ROLE_CREATE_CONCRETE.get("role_name")
    assert found_role.application_id == TEST_APPLICATION_ID_FAM
    # verify two roles are for different application
    assert second_concrete_role.role_id != new_concrete_role.role_id
    assert second_concrete_role.application_id != new_concrete_role.application_id
    assert second_concrete_role.role_name == new_concrete_role.role_name

    # create duplicate role, with another type and another user
    with pytest.raises(IntegrityError) as e:
        role_repo.create_role(
            {
                **TEST_ROLE_CREATE_CONCRETE,
                "create_user": TEST_ANOTHER_CREATER,
                "role_type_code": famConstants.RoleType.ROLE_TYPE_ABSTRACT,
            }
        )
    assert str(e.value).find(ERROR_VOLIATE_UNIQUE_CONSTRAINT) != -1


def test_create_child_role(role_repo: RoleRepository):
    # create child role with forest client number
    # remove the "forest_client_number" from the test data, as the role model doesn't have this field
    fam_role_dict = TEST_ROLE_CREATE_CHILD.model_dump()
    del fam_role_dict["forest_client_number"]
    new_child_role = role_repo.create_role(fam_role_dict)
    assert new_child_role.role_name == TEST_ROLE_CREATE_CHILD.role_name
    assert new_child_role.role_type_code == famConstants.RoleType.ROLE_TYPE_CONCRETE
    # verify child role created
    found_role = role_repo.get_role_by_id(new_child_role.role_id)
    assert found_role.role_id == new_child_role.role_id
    assert found_role.role_name == TEST_ROLE_CREATE_CHILD.role_name
    assert found_role.application_id == TEST_ROLE_CREATE_CHILD.application_id
    assert found_role.parent_role_id == TEST_ROLE_CREATE_CHILD.parent_role_id
    assert found_role.role_type_code == TEST_ROLE_CREATE_CHILD.role_type_code

    # create child role with invalid parent,
    # have to use a different application id to avoid duplication error and get the expect error
    with pytest.raises(IntegrityError) as e:
        role_repo.create_role(
            {
                **fam_role_dict,
                "application_id": TEST_APPLICATION_ID_FAM,
                "parent_role_id": TEST_NOT_EXIST_ROLE_ID,
            }
        )
    assert str(e.value).find(ERROR_VOLIATE_FOREIGN_KEY_CONSTRAINT) != -1
