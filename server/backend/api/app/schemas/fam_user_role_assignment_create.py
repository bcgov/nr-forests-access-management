
from datetime import datetime, timezone
from typing import List, Optional, Union

from api.app.constants import UserType
from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator
from typing_extensions import Annotated


# Role assignment with one role at a time for the user.
class FamUserRoleAssignmentCreateSchema(BaseModel):
    """
    Request schema for assigning a user to a role, with optional expiry date.
    Expiry date:
    - The date and time when the user role assignment expires.
    - If expiry date is provided, it must be in the future (BC timezone).
    - Null expiry date means no expiry.
    """
    user_name: Annotated[
        str, StringConstraints(min_length=3, max_length=20)
    ]  # IDIM search max length
    user_guid: Annotated[str, StringConstraints(min_length=32, max_length=32)]
    user_type_code: UserType
    role_id: int
    forest_client_numbers: Union[
        List[Annotated[str, StringConstraints(min_length=1, max_length=8)]], None
    ] = None
    requires_send_user_email: bool = False
    expiry_date: Optional[datetime] = None

    @field_validator('expiry_date')
    @classmethod
    def expiry_date_not_past(cls, v):
        if v is not None:
            now = datetime.now(timezone.utc)
            if v < now:
                raise ValueError('expiry_date must not be in the past')
        return v

    model_config = ConfigDict(from_attributes=True)
