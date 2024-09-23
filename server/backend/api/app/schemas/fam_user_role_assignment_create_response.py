from typing import Optional

from pydantic import BaseModel, ConfigDict

from .fam_application_user_role_assignment_get import \
    FamApplicationUserRoleAssignmentGetSchema


class FamUserRoleAssignmentCreateRes(BaseModel):
    status_code: int
    detail: FamApplicationUserRoleAssignmentGetSchema
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
