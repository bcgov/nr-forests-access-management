import logging

from api.app.crud import crud_access_control_privilege
from sqlalchemy.orm import Session
from testspg.constants import (
    FOM_DEV_APPLICATION_ID,
    TEST_USER_ID,
    FOM_DEV_REVIEWER_ROLE_ID,
)

LOGGER = logging.getLogger(__name__)


def test_is_delegated_admin_by_app_id(db_pg_session: Session):
    # we don't have a any access control privilege for FOM by default
    assert (
        crud_access_control_privilege.is_delegated_admin_by_app_id(
            db=db_pg_session,
            user_id=TEST_USER_ID,
            application_id=FOM_DEV_APPLICATION_ID,
        )
        is False
    )


def test_is_delegated_admin(db_pg_session: Session):
    # we don't have a any access control privilege for any user by default
    assert (
        crud_access_control_privilege.is_delegated_admin(
            db=db_pg_session,
            user_id=TEST_USER_ID,
        )
        is False
    )


def test_has_privilege_by_role_id(db_pg_session: Session):
    # we don't have a any access control privilege for any user by default
    assert (
        crud_access_control_privilege.has_privilege_by_role_id(
            db=db_pg_session,
            user_id=TEST_USER_ID,
            role_id=FOM_DEV_REVIEWER_ROLE_ID,
        )
        is False
    )
