import logging
from unittest.mock import MagicMock

import pytest
from api.app.schemas import schemas
from api.app.services.application_admin_service import ApplicationAdminService
from fastapi import HTTPException
from pydantic import ValidationError
from tests.constants import (TEST_CREATOR, TEST_INVALID_USER_TYPE,
                             TEST_NEW_APPLICATION_ADMIN)

LOGGER = logging.getLogger(__name__)


def test_create_application_admin(application_admin_service: ApplicationAdminService, new_idir_requester):

    application_admin_service.permission_audit_service.store_application_admin_permission_granted_audit_history = MagicMock()

    requester = new_idir_requester
    # test invalid user type
    with pytest.raises(ValidationError) as e:
        application_admin_service.create_application_admin(
            schemas.FamAppAdminCreateRequest(
                **{
                    "user_type_code": TEST_INVALID_USER_TYPE,
                    "user_name": TEST_NEW_APPLICATION_ADMIN.get("user_name"),
                    "application_id": TEST_NEW_APPLICATION_ADMIN.get("application_id"),
                }
            ),
            requester,
        )
    assert str(e.value).find("Input should be 'I' or 'B'") != -1

    # test create application admin
    mocked_admin_target_user = schemas.TargetUser(**TEST_NEW_APPLICATION_ADMIN)
    new_application_admin = application_admin_service.create_application_admin(
        schemas.FamAppAdminCreateRequest(**TEST_NEW_APPLICATION_ADMIN),
        mocked_admin_target_user,
        requester,
    )
    assert new_application_admin.application_id == TEST_NEW_APPLICATION_ADMIN.get(
        "application_id"
    )
    # verify the application admin is created
    application_admin = application_admin_service.get_application_admin_by_id(
        new_application_admin.application_admin_id
    )
    assert new_application_admin.user_id == application_admin.user_id
    assert new_application_admin.application_id == application_admin.application_id
    assert (
        new_application_admin.application_admin_id
        == application_admin.application_admin_id
    )

    # Verify audit history service is called
    application_admin_service.permission_audit_service.store_application_admin_permission_granted_audit_history.assert_called()

    # test create duplication application admin
    with pytest.raises(HTTPException) as e:
        application_admin_service.create_application_admin(
            schemas.FamAppAdminCreateRequest(**TEST_NEW_APPLICATION_ADMIN),
            mocked_admin_target_user,
            requester,
        )
    assert str(e._excinfo).find("User is admin already") != -1


def test_delete_application_admin(application_admin_service: ApplicationAdminService, new_idir_requester):
    application_admin_service.permission_audit_service.store_application_admin_permissions_revoked_audit_history = MagicMock()
    application_admin_service.application_admin_repo.delete_application_admin = MagicMock()

    requester = new_idir_requester
    test_application_admin_id = 1

    # Mock the deleted record
    mocked_deleted_record = MagicMock()
    mocked_deleted_record.application_admin_id = test_application_admin_id
    application_admin_service.application_admin_repo.delete_application_admin.return_value = mocked_deleted_record

    # Test delete application admin
    application_admin_service.delete_application_admin(requester, test_application_admin_id)

    # Verify the repository's delete method is called with the correct ID
    application_admin_service.application_admin_repo.delete_application_admin.assert_called_once_with(
        test_application_admin_id
    )

    # Verify the audit history service is called with the correct parameters
    application_admin_service.permission_audit_service.store_application_admin_permissions_revoked_audit_history.assert_called_once_with(
        requester, mocked_deleted_record
    )