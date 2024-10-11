import logging
from http import HTTPStatus

import pytest
from api.app.models.model import FamRole
from api.app.schemas import schemas
from api.app.services.access_control_privilege_service import \
    AccessControlPrivilegeService
from api.app.services.forest_client_service import ForestClientService
from api.app.services.role_service import RoleService
from api.app.services.user_service import UserService
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session
from tests.conftest import to_mocked_target_user
from tests.constants import (
    TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
    TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST_CONCRETE, TEST_CREATOR,
    TEST_FOM_DEV_REVIEWER_ROLE_ID, TEST_FOM_DEV_SUBMITTER_ROLE_ID,
    TEST_FOM_SUBMITTER_ROLE_NAME, TEST_FOREST_CLIENT_NUMBER,
    TEST_FOREST_CLIENT_NUMBER_TWO, TEST_INACTIVE_FOREST_CLIENT_NUMBER,
    TEST_INVALID_USER_TYPE, TEST_NON_EXIST_FOREST_CLIENT_NUMBER,
    TEST_NOT_EXIST_ROLE_ID, TEST_USER_ID)

LOGGER = logging.getLogger(__name__)


def test_grant_privilege(
    access_control_privilege_service: AccessControlPrivilegeService,
):
    # test handle a new access control privilege
    return_response = access_control_privilege_service.grant_privilege(
        TEST_USER_ID,
        TEST_FOM_DEV_SUBMITTER_ROLE_ID,
        TEST_CREATOR,
    )
    assert return_response.status_code == HTTPStatus.OK
    assert return_response.detail.user_id == TEST_USER_ID
    assert return_response.detail.role_id == TEST_FOM_DEV_SUBMITTER_ROLE_ID

    # verify the access control is created
    new_record = access_control_privilege_service.get_acp_by_user_id_and_role_id(
        TEST_USER_ID, TEST_FOM_DEV_SUBMITTER_ROLE_ID
    )
    assert new_record.user_id == TEST_USER_ID
    assert new_record.role_id == TEST_FOM_DEV_SUBMITTER_ROLE_ID

    # test create duplication access control privilege
    return_response = access_control_privilege_service.grant_privilege(
        TEST_USER_ID,
        TEST_FOM_DEV_SUBMITTER_ROLE_ID,
        TEST_CREATOR,
    )
    assert return_response.status_code == HTTPStatus.CONFLICT
    assert return_response.detail.user_id == TEST_USER_ID
    assert return_response.detail.role_id == TEST_FOM_DEV_SUBMITTER_ROLE_ID
    assert (
        str(return_response.error_message).find(
            "User already has the requested access control privilege"
        )
        != -1
    )


def test_create_access_control_privilege_many(
    access_control_privilege_service: AccessControlPrivilegeService,
    user_service: UserService,
    forest_client_service: ForestClientService,
    db_pg_session: Session,
    new_idir_requester,
):
    # verify the new user does not exist
    found_user = user_service.get_user_by_domain_and_name(
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST_CONCRETE.get("user_name"),
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST_CONCRETE.get("user_type_code"),
    )
    assert found_user is None
    requester = new_idir_requester
    # test create access control privilege for concrete role without forest client number
    return_result = (
        access_control_privilege_service.create_access_control_privilege_many(
            schemas.FamAccessControlPrivilegeCreateRequest(
                **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST_CONCRETE
            ),
            requester,
            to_mocked_target_user(
                TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST_CONCRETE
            )
        )
    )
    assert len(return_result) == 1
    assert return_result[0].status_code == HTTPStatus.OK
    assert return_result[0].detail.role_id == TEST_FOM_DEV_REVIEWER_ROLE_ID
    # verify the new user is created
    new_user = user_service.get_user_by_domain_and_name(
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST_CONCRETE.get("user_type_code"),
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST_CONCRETE.get("user_name"),
    )
    assert (
        new_user.user_name
        == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST_CONCRETE.get("user_name")
    )
    NEW_USER_ID = new_user.user_id
    assert return_result[0].detail.user_id == NEW_USER_ID
    # verify the access control privilege is created
    new_record = access_control_privilege_service.get_acp_by_user_id_and_role_id(
        NEW_USER_ID, TEST_FOM_DEV_REVIEWER_ROLE_ID
    )
    assert new_record.user_id == NEW_USER_ID
    assert new_record.role_id == TEST_FOM_DEV_REVIEWER_ROLE_ID

    # test create access control privilege for abstract parent role with single forest client number
    return_result = (
        access_control_privilege_service.create_access_control_privilege_many(
            schemas.FamAccessControlPrivilegeCreateRequest(
                **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST
            ),
            requester,
            to_mocked_target_user(
                TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST
            )
        )
    )
    assert len(return_result) == 1
    assert return_result[0].status_code == HTTPStatus.OK
    assert return_result[0].detail.user_id == NEW_USER_ID
    # verify the new forest client number is created
    new_forest_client = forest_client_service.get_forest_client_by_number(
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST.get("forest_client_numbers")[0]
    )
    assert (
        new_forest_client.forest_client_number
        == TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST.get("forest_client_numbers")[0]
    )
    # verify the new child role is created
    new_child_role: FamRole = (
        db_pg_session.query(FamRole)
        .filter(FamRole.client_number_id == new_forest_client.client_number_id)
        .one_or_none()
    )
    assert new_child_role.role_name == RoleService.construct_forest_client_role_name(
        TEST_FOM_SUBMITTER_ROLE_NAME,
        TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST.get("forest_client_numbers")[0],
    )
    NEW_ROLE_ID = new_child_role.role_id
    assert return_result[0].detail.role_id == NEW_ROLE_ID
    # verify the access control privilege is created
    new_record = access_control_privilege_service.get_acp_by_user_id_and_role_id(
        NEW_USER_ID, NEW_ROLE_ID
    )
    assert new_record.user_id == NEW_USER_ID
    assert new_record.role_id == NEW_ROLE_ID

    # test create access control privilege for abstract parent role with 2 forest client numbers,
    # one already created in the above step, one is new
    return_result = (
        access_control_privilege_service.create_access_control_privilege_many(
            schemas.FamAccessControlPrivilegeCreateRequest(
                **{
                    **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
                    "forest_client_numbers": [
                        TEST_FOREST_CLIENT_NUMBER,
                        TEST_FOREST_CLIENT_NUMBER_TWO,
                    ],
                }
            ),
            requester,
            to_mocked_target_user(
                TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST
            )
        )
    )
    assert len(return_result) == 2
    assert return_result[0].status_code == HTTPStatus.CONFLICT
    assert return_result[0].detail.user_id == NEW_USER_ID
    assert return_result[0].detail.role_id == NEW_ROLE_ID
    assert (
        str(return_result[0].error_message).find(
            "User already has the requested access control privilege"
        )
        != -1
    )
    assert return_result[1].status_code == HTTPStatus.OK
    assert return_result[1].detail.user_id == NEW_USER_ID
    new_child_role_two: FamRole = (
        db_pg_session.query(FamRole)
        .filter(
            FamRole.role_name
            == RoleService.construct_forest_client_role_name(
                TEST_FOM_SUBMITTER_ROLE_NAME,
                TEST_FOREST_CLIENT_NUMBER_TWO,
            )
        )
        .one_or_none()
    )
    NEW_ROLE_ID_TWO = new_child_role_two.role_id
    assert return_result[1].detail.role_id == new_child_role_two.role_id
    # verify new access control privilege is created
    new_record = access_control_privilege_service.get_acp_by_user_id_and_role_id(
        NEW_USER_ID, NEW_ROLE_ID_TWO
    )
    assert new_record.user_id == NEW_USER_ID
    assert new_record.role_id == NEW_ROLE_ID_TWO

    # test create access control privilege for abstract parent role without forest client number
    with pytest.raises(HTTPException) as e:
        copy_data = {**TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST}
        del copy_data["forest_client_numbers"]
        access_control_privilege_service.create_access_control_privilege_many(
            schemas.FamAccessControlPrivilegeCreateRequest(**copy_data),
            requester,
            to_mocked_target_user(
                TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST
            )
        )
    assert (
        str(e._excinfo).find(
            "Invalid access control privilege request, missing forest client number."
        )
        != -1
    )


def test_create_access_control_privilege_many_invalid_user_type(
    access_control_privilege_service: AccessControlPrivilegeService,
):
    # test create access control privilege with invalid user type
    with pytest.raises(ValidationError) as e:
        access_control_privilege_service.create_access_control_privilege_many(
            schemas.FamAccessControlPrivilegeCreateRequest(
                **{
                    **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
                    "user_type_code": TEST_INVALID_USER_TYPE,
                }
            ),
            TEST_CREATOR,
        )
    assert str(e.value).find("Input should be 'I' or 'B'") != -1


def test_create_access_control_privilege_many_invalid_role_id(
    access_control_privilege_service: AccessControlPrivilegeService,
    new_idir_requester
):
    # test create access control privilege with non exists role id
    with pytest.raises(HTTPException) as e:
        access_control_privilege_service.create_access_control_privilege_many(
            schemas.FamAccessControlPrivilegeCreateRequest(
                **{
                    **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
                    "role_id": TEST_NOT_EXIST_ROLE_ID,
                }
            ),
            new_idir_requester,
            to_mocked_target_user(
                TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST
            )
        )
    error_msg = f"Role id {TEST_NOT_EXIST_ROLE_ID} does not exist."
    assert str(e._excinfo).find(error_msg) != -1


def test_create_access_control_privilege_many_invalid_forest_client(
    access_control_privilege_service: AccessControlPrivilegeService,
    new_idir_requester
):
    with pytest.raises(HTTPException) as e:
        access_control_privilege_service.create_access_control_privilege_many(
            schemas.FamAccessControlPrivilegeCreateRequest(
                **{
                    **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
                    "forest_client_numbers": [TEST_NON_EXIST_FOREST_CLIENT_NUMBER],
                }
            ),
            new_idir_requester,
            to_mocked_target_user(
                TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST
            )
        )
    assert (
        str(e._excinfo).find(
            f"Forest client number {TEST_NON_EXIST_FOREST_CLIENT_NUMBER} does not exist"
        )
        != -1
    )


def test_create_access_control_privilege_many_inactive_forest_client(
    access_control_privilege_service: AccessControlPrivilegeService,
    new_idir_requester
):
    with pytest.raises(HTTPException) as e:
        access_control_privilege_service.create_access_control_privilege_many(
            schemas.FamAccessControlPrivilegeCreateRequest(
                **{
                    **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
                    "forest_client_numbers": [TEST_INACTIVE_FOREST_CLIENT_NUMBER],
                }
            ),
            new_idir_requester,
            to_mocked_target_user(
                TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST
            )
        )
    assert (
        str(e._excinfo).find(
            f"Forest client number {TEST_INACTIVE_FOREST_CLIENT_NUMBER} is not in active status"
        )
        != -1
    )


def test_create_access_control_privilege_many_active_and_inactive_forest_client(
    access_control_privilege_service: AccessControlPrivilegeService,
    new_idir_requester
):
    # test create access control privilege for abstract parent role with 3 forest client numbers,
    # one is inactive, one is active, one is invalid
    with pytest.raises(HTTPException) as e:
        access_control_privilege_service.create_access_control_privilege_many(
            schemas.FamAccessControlPrivilegeCreateRequest(
                **{
                    **TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST,
                    "forest_client_numbers": [
                        TEST_FOREST_CLIENT_NUMBER,
                        TEST_INACTIVE_FOREST_CLIENT_NUMBER,
                        TEST_NON_EXIST_FOREST_CLIENT_NUMBER,
                    ],
                }
            ),
            new_idir_requester,
            to_mocked_target_user(
                TEST_ACCESS_CONTROL_PRIVILEGE_CREATE_REQUEST
            )
        )
    assert (
        str(e._excinfo).find(
            f"Forest client number {TEST_INACTIVE_FOREST_CLIENT_NUMBER} is not in active status"
        )
        != -1
    )
