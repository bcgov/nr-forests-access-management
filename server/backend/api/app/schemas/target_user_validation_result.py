
from typing import List
from pydantic import BaseModel
from api.app.schemas import TargetUserSchema


class FailedTargetUserSchema(TargetUserSchema):
    """
    Represents a target user that failed validation. Includes the reason for failure.
    """
    error_reason: str

class TargetUserValidationResultSchema(BaseModel):
    """
    Represents the result of validating a list of target users.

    - verified_users: Users who exist and passed external identity checks (e.g., IDIM web service).
    - failed_users: Users who could not be verified or failed validation checks, with error details.
    """
    verified_users: List[TargetUserSchema]
    failed_users: List[FailedTargetUserSchema]
