from typing import Optional

from api.app.constants import (EMAIL_MAX_LEN, FIRST_NAME_MAX_LEN,
                               LAST_NAME_MAX_LEN, SYSTEM_ACCOUNT_NAME,
                               USER_NAME_MAX_LEN)
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator
from typing_extensions import Annotated


class PrivilegeChangePerformerSchema(BaseModel):
    """
    This schema represents the structure of the `change_user_details` JSON field used in fam_privilege_change_audit.

    The `change_user_details` field captures information about the user who performed a change, including
    the `username`, `first_name`, `last_name`, and `email`. It is used to record the user details at the time
    of the audit event, ensuring that changes to these details later do not affect the integrity of the audit log.

    For regular users, all fields (`username`, `first_name`, `last_name`, and `email`) are included. However,
    when the change is performed by a system account, only the `username` field is present, and it is set to
    "system". The schema includes validation logic to enforce this rule.

    Attributes:
        username (str): The username of the user performing the change. For system accounts, this is "system".
        first_name (str, optional): The first name of the user. Not present for system accounts.
        last_name (str, optional): The last name of the user. Not present for system accounts.
        email (str, optional): The email address of the user. Not present for system accounts.

    Validation:
        The schema includes a validator to ensure that for system accounts (where `username` is "system"),
        no other fields (`first_name`, `last_name`, `email`) are populated.
    """

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

        if username == SYSTEM_ACCOUNT_NAME:
            # For system accounts, only username should be present
            if first_name or last_name or email:
                raise ValueError("System account should only have a username.")
        # For regular users, no additional checks are needed; username is the only required field.

        return values
