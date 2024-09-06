from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, StringConstraints
from typing_extensions import Annotated

from api.app.constants import FIRST_NAME_MAX_LEN, LAST_NAME_MAX_LEN


class GCNotifyGrantAccessEmailParamSchema(BaseModel):
    first_name: Optional[
        Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    ] = None
    last_name: Optional[
        Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    ] = None
    application_name: Annotated[str, StringConstraints(max_length=35)]
    role_list_string: Annotated[str, StringConstraints(max_length=500)]
    application_team_contact_email: Optional[EmailStr] = None
    send_to_email: EmailStr
    with_client_number: Literal["yes", "no"]
