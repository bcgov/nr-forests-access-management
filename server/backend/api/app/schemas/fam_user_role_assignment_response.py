from typing import List

from pydantic import BaseModel

from .fam_user_role_assignment_create_response import \
    FamUserRoleAssignmentCreateRes


class FamUserRoleAssignmentRes(BaseModel):
    assignments_detail: List[FamUserRoleAssignmentCreateRes]
