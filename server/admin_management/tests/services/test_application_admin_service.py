import logging
import pytest
from pydantic import ValidationError
from fastapi import HTTPException

from api.app import schemas
from api.app.services.application_admin_service import ApplicationAdminService

from tests.constants import (
    TEST_NEW_APPLICATION_ADMIN,
    TEST_CREATOR,
    TEST_NOT_INVALID_USER_TYPE,
)


LOGGER = logging.getLogger(__name__)


def test_create_application_admin(application_admin_service: ApplicationAdminService):
    # test invalid user type
    with pytest.raises(ValidationError) as e:
        application_admin_service.create_application_admin(
            schemas.FamAppAdminCreate(
                **{
                    "user_type_code": TEST_NOT_INVALID_USER_TYPE,
                    "user_name": TEST_NEW_APPLICATION_ADMIN.get("user_name"),
                    "application_id": TEST_NEW_APPLICATION_ADMIN.get("application_id"),
                }
            ),
            TEST_CREATOR,
        )
    assert str(e.value).find("Input should be 'I' or 'B'") != -1

    # test create application admin
    new_application_admin = application_admin_service.create_application_admin(
        schemas.FamAppAdminCreate(**TEST_NEW_APPLICATION_ADMIN),
        TEST_CREATOR,
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
            schemas.FamAppAdminCreate(**TEST_NEW_APPLICATION_ADMIN),
            TEST_CREATOR,
        )
    assert str(e._excinfo).find("User is admin already") != -1