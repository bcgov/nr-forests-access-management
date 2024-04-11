import logging

from api.app.crud import crud_access_control_privilege
from sqlalchemy.orm import Session
from testspg.constants import (
    TEST_FOM_DEV_APPLICATION_ID,
    TEST_USER_ID,
)

LOGGER = logging.getLogger(__name__)


def test_get_delegated_admin_by_user_and_app_id(db_pg_session: Session):
    access_control_privileges = (
        crud_access_control_privilege.get_delegated_admin_by_user_and_app_id(
            db=db_pg_session,
            user_id=TEST_USER_ID,
            application_id=TEST_FOM_DEV_APPLICATION_ID,
        )
    )
    # we don't have a any access control privilege for FOM by default
    assert len(access_control_privileges) == 0


def test_get_delegated_admin_by_user_id(db_pg_session: Session):
    access_control_privileges = (
        crud_access_control_privilege.get_delegated_admin_by_user_id(
            db=db_pg_session,
            user_id=TEST_USER_ID,
        )
    )
    # we don't have a any access control privilege for any user by default
    assert len(access_control_privileges) == 0