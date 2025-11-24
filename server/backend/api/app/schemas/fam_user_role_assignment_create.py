
from datetime import datetime, time, timezone
from typing import List, Optional, Union
from zoneinfo import ZoneInfo

from api.app.constants import UserType
from pydantic import (BaseModel, ConfigDict, GetCoreSchemaHandler,
                      StringConstraints, field_validator)
from typing_extensions import Annotated


# Role assignment with one role at a time for the user.
class FamUserRoleAssignmentCreateSchema(BaseModel):
    """
    Request schema for assigning a user to a role, with optional expiry date.
    - expiry_date_date: The expiry date as a string (YYYY-MM-DD), BC timezone.
    - expiry_date: Internal use, timezone-aware datetime, derived from expiry_date_date.
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
    expiry_date: Optional[datetime] = None  # internal use only.

    @classmethod
    def __get_pydantic_core_schema__(cls, *args, **kwargs):
        schema = super().__get_pydantic_core_schema__(*args, **kwargs)
        if hasattr(schema, 'fields'):
            # Hide expiry_date from OpenAPI/Swagger. We use this field internally only.
            schema.fields.pop('expiry_date', None)
        return schema


    @field_validator('expiry_date_date')
    @classmethod
    def validate_expiry_date_date(cls, v):
        if v is None:
            return v
        bc_tz = ZoneInfo('America/Vancouver')
        try:
            d = datetime.strptime(v, '%Y-%m-%d').date()
        except Exception:
            raise ValueError('expiry_date_date must be a valid YYYY-MM-DD string')
        dt = datetime.combine(d, time(0, 0, 0)).replace(tzinfo=bc_tz)
        now_bc = datetime.now(bc_tz)
        if dt < now_bc:
            raise ValueError('expiry_date_date must not be in the past (BC timezone)')
        return v

    @classmethod
    def model_validate(cls, value, *args, **kwargs):
        obj = super().model_validate(value, *args, **kwargs)
        if obj.expiry_date_date:
            bc_tz = ZoneInfo('America/Vancouver')
            d = datetime.strptime(obj.expiry_date_date, '%Y-%m-%d').date()
            obj.expiry_date = datetime.combine(d, time(0, 0, 0)).replace(tzinfo=bc_tz)
        else:
            obj.expiry_date = None
        return obj

    model_config = ConfigDict(from_attributes=True)
