from typing import Optional

from pydantic import BaseModel, ConfigDict
from api.app.constants import EmailSendingStatus

from .fam_application_user_role_assignment_get import \
    FamApplicationUserRoleAssignmentGetSchema


class FamUserRoleAssignmentCreateRes(BaseModel):
    status_code: int
    detail: Optional[FamApplicationUserRoleAssignmentGetSchema] = None
    error_message: Optional[str] = None
    email_sending_status: EmailSendingStatus = EmailSendingStatus.NOT_REQUIRED

    model_config = ConfigDict(from_attributes=True)
