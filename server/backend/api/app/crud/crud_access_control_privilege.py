import logging
from typing import List

from api.app.models.model import FamAccessControlPrivilege, FamRole
from sqlalchemy.orm import Session


LOGGER = logging.getLogger(__name__)


def is_delegated_admin_by_app_id(
    db: Session, user_id: int, application_id: int
) -> bool:
    """
    Find out from `app_fam.fam_access_control_privilege` if user is the delegated admin of the application.

    :param user_id: primary id that is associated with the user.
    :param application_id: primary id that is associated with the application.
    :return: true if there is at least one record, false if no record
    """
    return (
        True
        if db.query(FamAccessControlPrivilege)
        .join(FamRole)
        .filter(
            FamAccessControlPrivilege.user_id == user_id,
            FamRole.application_id == application_id,
        )
        .first()
        else False
    )


def is_delegated_admin(db: Session, user_id: int) -> bool:
    """
    Find out from `app_fam.fam_access_control_privilege` if user is the delegated admin of any application.

    :param user_id: primary id that is associated with the user.
    :return: true if there is at least one record, false if no record
    """
    return (
        True
        if db.query(FamAccessControlPrivilege)
        .filter(
            FamAccessControlPrivilege.user_id == user_id,
        )
        .first()
        else False
    )


def has_privilege_by_role_id(db: Session, user_id: int, role_id: int) -> bool:
    """
    Find out from `app_fam.fam_access_control_privilege` if user is the delegated admin of any application.

    :param user_id: primary id that is associated with the user.
    :param role_id: primary id that is associated with the role.
    :return: true if there is the record, false if no record
    """
    return (
        True
        if db.query(FamAccessControlPrivilege)
        .filter(
            FamAccessControlPrivilege.user_id == user_id,
            FamAccessControlPrivilege.role_id == role_id,
        )
        .one_or_none()
        else False
    )
