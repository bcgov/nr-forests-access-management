from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, StringConstraints
from typing_extensions import Annotated


class GCNotifyGrantAccessEmailParamSchema(BaseModel):
    first_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    application_name: Annotated[str, StringConstraints(max_length=35)]
    role_list_string: Annotated[str, StringConstraints(max_length=500)]
    application_team_contact_email: Optional[EmailStr] = None
    send_to_email: EmailStr
    with_client_number: Literal["yes", "no"]
