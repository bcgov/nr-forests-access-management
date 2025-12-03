
import logging
from datetime import datetime, time
from typing import List, Optional, Union
from zoneinfo import ZoneInfo

from api.app.constants import UserType
from api.app.datetime_format import BC_TIMEZONE, DATE_FORMAT_YYYY_MM_DD
from pydantic import (BaseModel, ConfigDict, PrivateAttr, StringConstraints,
                      field_validator, model_validator)
from typing_extensions import Annotated

LOGGER = logging.getLogger(__name__)

# Role assignment with one role at a time for the user.
class FamUserRoleAssignmentCreateSchema(BaseModel):
    """
    Request schema for assigning a user to a role, with optional expiry date.
    - expiry_date_date: The expiry date as a string (YYYY-MM-DD), BC timezone.
    - _expiry_date: Internal use only, timezone-aware datetime, derived from expiry_date_date.
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
    expiry_date_date: Optional[str] = None  # e.g. '2025-12-31', BC timezone.
    # Internal use only, not exposed in OpenAPI or request/response bodies
    _expiry_date: Optional[datetime] = PrivateAttr(default=None)


    @field_validator('expiry_date_date')
    @classmethod
    def validate_expiry_date_date(cls, v):
        if v is None:
            return v
        if isinstance(v, str) and v.strip() == "":
            return None
        bc_tz = ZoneInfo(BC_TIMEZONE)
        try:
            dv = datetime.strptime(v, DATE_FORMAT_YYYY_MM_DD).date()
        except Exception:
            raise ValueError('expiry_date_date must be a valid YYYY-MM-DD string')
        now_bc = datetime.now(bc_tz).date()
        if dv < now_bc:
            raise ValueError('expiry_date_date must be today or in the future (BC timezone)')
        return v


    @model_validator(mode="after")
    def set_expiry_date(self):
        if self.expiry_date_date:
            bc_tz = ZoneInfo(BC_TIMEZONE)
            d = datetime.strptime(self.expiry_date_date, DATE_FORMAT_YYYY_MM_DD).date()
            # Set expiry to end of day (23:59:59) in BC timezone
            self._expiry_date = datetime.combine(d, time(23, 59, 59)).replace(tzinfo=bc_tz)
            LOGGER.debug(f"Set internal _expiry_date to {self._expiry_date} based on expiry_date_date {self.expiry_date_date}")
        else:
            self._expiry_date = None
        return self

    model_config = ConfigDict(from_attributes=True)
