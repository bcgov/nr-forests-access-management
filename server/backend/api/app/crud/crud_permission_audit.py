from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy import desc  # Import if you want descending order
from typing import List
from api.app.models.model import FamPrivilegeChangeAudit
from api.app.schemas import PermissionAuditHistoryResDto

def read_permission_audit_history_by_user_and_application(
    user_id: int, application_id: int, db: Session
) -> List[PermissionAuditHistoryResDto]:
    """
    Retrieve the permission audit history for a given user and application,
    ordered by the date of the change.

    :param user_id: The ID of the user whose permission changes are being queried.
    :param application_id: The ID of the application associated with the permission changes.
    :param db: The database session used for querying.
    :return: A list of PermissionAuditHistoryResDto instances representing the audit history records.
    """

    # Query the FamPrivilegeChangeAudit table for records matching the user_id and application_id,
    # and order the results by change_date (most recent first).
    audit_history_records = db.query(FamPrivilegeChangeAudit).filter(
        and_(
            FamPrivilegeChangeAudit.change_target_user_id == user_id,
            FamPrivilegeChangeAudit.application_id == application_id,
        )
    ).order_by(FamPrivilegeChangeAudit.change_date.desc()).all()  # Order by change_date, descending

    # Convert the ORM model instances to Pydantic DTO instances
    audit_history_dto = [
        PermissionAuditHistoryResDto(
            change_date=record.change_date,
            change_performer_user_details=record.change_performer_user_details,
            change_performer_user_id=record.change_performer_user_id,
            change_target_user_id=record.change_target_user_id,
            create_date=record.create_date,
            create_user=record.create_user,
            privilege_change_type_code=record.privilege_change_type_code,
            privilege_details=record.privilege_details,
        )
        for record in audit_history_records
    ]

    return audit_history_dto