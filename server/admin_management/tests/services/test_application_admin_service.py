import logging

import pytest
from api.app.schemas import schemas
from api.app.services.application_admin_service import ApplicationAdminService
from fastapi import HTTPException
from pydantic import ValidationError
from tests.constants import (TEST_CREATOR, TEST_INVALID_USER_TYPE,
                             TEST_NEW_APPLICATION_ADMIN)

LOGGER = logging.getLogger(__name__)


def test_create_application_admin(application_admin_service: ApplicationAdminService, new_idir_requester):
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

    # test create duplication application admin
    with pytest.raises(HTTPException) as e:
        application_admin_service.create_application_admin(
            schemas.FamAppAdminCreateRequest(**TEST_NEW_APPLICATION_ADMIN),
            mocked_admin_target_user,
            requester,
        )
    assert str(e._excinfo).find("User is admin already") != -1
