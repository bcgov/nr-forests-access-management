from typing import List, Literal, Optional

from api.app.constants import (APPLICATION_DESC_MAX_LEN, FIRST_NAME_MAX_LEN,
                               LAST_NAME_MAX_LEN, ROLE_NAME_MAX_LEN,
                               USER_NAME_MAX_LEN)
from api.app.schemas.fam_forest_client import FamForestClientSchema
from pydantic import BaseModel, EmailStr, StringConstraints
from typing_extensions import Annotated


class GCNotifyGrantAccessEmailParamSchema(BaseModel):
    user_name: Annotated[str, StringConstraints(max_length=USER_NAME_MAX_LEN)]
    first_name: Optional[
        Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    ] = None
    last_name: Optional[
        Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    ] = None
    # Email param variable is application_name but should supply application_description as data.
    application_description: Annotated[str, StringConstraints(max_length=APPLICATION_DESC_MAX_LEN)]
    # Allow sending with 1 role and scope with multiple organization (optional)
    role_display_name: Annotated[str, StringConstraints(max_length=ROLE_NAME_MAX_LEN)]
    organization_list: Optional[List[FamForestClientSchema]] = None
    application_team_contact_email: Optional[EmailStr] = None
    send_to_email: EmailStr
