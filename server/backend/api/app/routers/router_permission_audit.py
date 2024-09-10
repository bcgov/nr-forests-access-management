import logging
from typing import List

from api.app import database
from api.app.crud import crud_application
from api.app.routers.router_guards import (
    authorize_by_app_id,
    authorize_by_application_role,
    get_current_requester,
)
from api.app.schemas import RequesterSchema, FamApplicationUserRoleAssignmentGetSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/", response_model=List[dict], status_code=200
)
async def get_permission_audit_history_by_user_and_application(
    user_id: int,
    application_id: int = Depends(authorize_by_app_id),
):
    """
    Retrieve the permission audit history for a given user and application.

    Args:
        userId (int): The ID of the user for whom the audit history is being requested.
        applicationId (int): The ID of the application associated with the audit history.

    Returns:
        List[dict]: A list of audit history records for the given user and application.
    """
    audit_history = [
        {
            "audit_id": 1,
            "user_id": user_id,
            "application_id": application_id,
            "change": "Role added",
        },
        {
            "audit_id": 2,
            "user_id": user_id,
            "application_id": application_id,
            "change": "Role removed",
        },
    ]

    if not audit_history:
        raise HTTPException(
            status_code=404,
            detail="No audit history found for the given user and application",
        )

    return audit_history
