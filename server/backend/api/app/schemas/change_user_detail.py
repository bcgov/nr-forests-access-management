from typing import Optional
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator
from typing_extensions import Annotated

from api.app.constants import (
    USER_NAME_MAX_LEN,
    FIRST_NAME_MAX_LEN,
    LAST_NAME_MAX_LEN,
    EMAIL_MAX_LEN,
)


class ChangeUserDetailsSchema(BaseModel):
    username: Annotated[str, StringConstraints(max_length=USER_NAME_MAX_LEN)]
    first_name: Optional[
        Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    ] = None
    last_name: Optional[
        Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    ] = None
    email: Optional[Annotated[str, StringConstraints(max_length=EMAIL_MAX_LEN)]] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def validate_user_details(cls, values):
        username = values.get("username")
        first_name = values.get("first_name")
        last_name = values.get("last_name")
        email = values.get("email")

        if username == "system":
            # For system accounts, only username should be present
            if first_name or last_name or email:
                raise ValueError("System account should only have a username.")
        # For regular users, no additional checks are needed; username is the only required field.

        return values
