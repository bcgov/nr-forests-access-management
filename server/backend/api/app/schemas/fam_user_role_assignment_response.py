from typing import List
from pydantic import BaseModel
from api.app.constants import EmailSendingStatus
from .fam_user_role_assignment_create_response import (
    FamUserRoleAssignmentCreateResponseSchema,
)


class FamUserRoleAssignmentResponseSchema(BaseModel):
    email_sending_status: EmailSendingStatus = EmailSendingStatus.NOT_REQUIRED
    assignments_detail: List[FamUserRoleAssignmentCreateResponseSchema]
