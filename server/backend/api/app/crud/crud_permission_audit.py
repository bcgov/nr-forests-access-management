from typing import List

from api.app.models.model import FamPrivilegeChangeAudit
from api.app.schemas import PermissionAduitHistoryRes
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload


def read_permission_audit_history_by_user_and_application(
    user_id: int, application_id: int, db: Session
) -> List[PermissionAduitHistoryRes]:
    """
    Retrieve the permission audit history for a given user and application,
    ordered by the date of the change.

    :param user_id: The ID of the user whose permission changes are being queried.
    :param application_id: The ID of the application associated with the permission changes.
    :param db: The database session used for querying.
    :return: A list of PermissionAduitHistoryRes instances representing the audit history records.
    """

    # Query the FamPrivilegeChangeAudit table for records matching the user_id and application_id,
    # and order the results by change_date (most recent first).
    audit_history_records = (
        db.query(FamPrivilegeChangeAudit)
        .filter(
            and_(
                FamPrivilegeChangeAudit.change_target_user_id == user_id,
                FamPrivilegeChangeAudit.application_id == application_id,
            )
        )
        .options(joinedload(FamPrivilegeChangeAudit.privilege_change_type))
        .order_by(FamPrivilegeChangeAudit.change_date.desc())
        .all()
    )

    # Convert the ORM model instances to Pydantic DTO instances
    audit_history_dto = [
        PermissionAduitHistoryRes.model_validate(
            {
                **record.__dict__,
                "privilege_change_type_description": record.privilege_change_type.description
            }
        )
        for record in audit_history_records
    ]

    return audit_history_dto
