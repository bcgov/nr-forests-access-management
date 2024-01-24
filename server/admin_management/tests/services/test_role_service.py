import logging

from api.app.services.forest_client_service import ForestClientService
from api.app.services.role_service import RoleService
from tests.constants import (
    TEST_ROLE_CREATE_CHILD,
    TEST_FOREST_CLIENT_NUMBER,
    TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    TEST_CREATOR,
    TEST_FOM_SUBMITTER_ROLE_NAME,
)


LOGGER = logging.getLogger(__name__)


def test_create_role(
    role_service: RoleService, forest_client_service: ForestClientService
):
    # ignore the test for creating concrete role and abstract role
    # cause we already did at repository level, and there is no difference
    # test create chile role with forest client number
    new_child_role = role_service.create_role(TEST_ROLE_CREATE_CHILD)
    assert new_child_role.role_name == TEST_ROLE_CREATE_CHILD.role_name
    # verify child role is created
    found_role = role_service.get_role_by_id(new_child_role.role_id)
    assert found_role.role_id == new_child_role.role_id
    assert found_role.role_name == TEST_ROLE_CREATE_CHILD.role_name
    assert found_role.application_id == TEST_ROLE_CREATE_CHILD.application_id
    assert found_role.parent_role_id == TEST_ROLE_CREATE_CHILD.parent_role_id
    assert found_role.role_type_code == TEST_ROLE_CREATE_CHILD.role_type_code
    # verify forest client number record is created
    found_forest_client = forest_client_service.get_forest_client_by_number(
        TEST_FOREST_CLIENT_NUMBER
    )
    assert found_forest_client is not None
    assert found_forest_client.client_number_id == found_role.client_number_id
    assert found_forest_client.create_user == found_role.create_user


def test_find_or_create_forest_client_child_role(role_service: RoleService):
    # create child role for abstract parent role
    test_role = role_service.get_role_by_id(TEST_FOM_DEV_SUBMITTER_ROLE_ID)
    result = role_service.find_or_create_forest_client_child_role(
        TEST_FOREST_CLIENT_NUMBER, test_role, TEST_CREATOR
    )
    # verify child role created
    child_role_one = role_service.get_role_by_id(result.role_id)
    assert child_role_one.role_id == result.role_id
    assert child_role_one.role_name == RoleService.construct_forest_client_role_name(
        TEST_FOM_SUBMITTER_ROLE_NAME, TEST_FOREST_CLIENT_NUMBER
    )
