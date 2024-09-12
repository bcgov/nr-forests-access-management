import logging
from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from api.app import database
from api.app.routers.router_guards import authorize_by_app_id
from api.app.schemas import PermissionAuditHistoryResDto
from api.app.crud.crud_permission_audit import (
    read_permission_audit_history_by_user_and_application,
)

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[PermissionAuditHistoryResDto], status_code=200)
async def get_permission_audit_history_by_user_and_application(
    user_id: int,
    application_id: int = Depends(authorize_by_app_id),
    db: Session = Depends(database.get_db),
):
    """
    Retrieve the permission audit history for a given user and application.

    Args:
        userId (int): The ID of the user for whom the audit history is being requested.
        applicationId (int): The ID of the application associated with the audit history.

    Returns:
        List[PermissionAuditHistoryResDto]: A list of audit history records for the given user and application.
    """
    return read_permission_audit_history_by_user_and_application(
        user_id=user_id, application_id=application_id, db=db
    )
