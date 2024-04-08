import logging
from typing import List

from api.app.models.model import FamAccessControlPrivilege, FamRole
from sqlalchemy.orm import Session


LOGGER = logging.getLogger(__name__)


def get_delegated_admin_by_user_and_app_id(
    db: Session, user_id: int, application_id: int
) -> FamAccessControlPrivilege:
    """
    Find out from `app_fam.fam_access_control_privilege` if user is the delegated admin of the application.

    :param user_id: primary id that is associated with the user.
    :param application_id: primary id that is associated with the application.
    :return: FamAccessControlPrivilege record, role information the user is able to manage
    """
    return (
        db.query(FamAccessControlPrivilege)
        .join(FamRole)
        .filter(
            FamAccessControlPrivilege.user_id == user_id,
            FamRole.application_id == application_id,
        )
        .one_or_none()
    )


def get_delegated_admin_by_user_id(
    db: Session, user_id: int
) -> List[FamAccessControlPrivilege]:
    """
    Find out from `app_fam.fam_access_control_privilege` if user is the delegated admin of any application.

    :param user_id: primary id that is associated with the user.
    :return: FamAccessControlPrivilege records, role information the user is able to manage
    """
    return (
        db.query(FamAccessControlPrivilege)
        .filter(
            FamAccessControlPrivilege.user_id == user_id,
        )
        .all()
    )


def get_delegated_admin_by_user_id_and_role_id(
    db: Session, user_id: int, role_id: int
) -> List[FamAccessControlPrivilege]:
    """
    Find out from `app_fam.fam_access_control_privilege` if user is the delegated admin of any application.

    :param user_id: primary id that is associated with the user.
    :return: FamAccessControlPrivilege records, role information the user is able to manage
    """
    return (
        db.query(FamAccessControlPrivilege)
        .filter(
            FamAccessControlPrivilege.user_id == user_id,
            FamAccessControlPrivilege.role_id == role_id,
        )
        .one_or_none()
    )
