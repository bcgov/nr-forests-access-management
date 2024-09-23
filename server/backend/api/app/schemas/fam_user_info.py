from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from api.app.constants import (
    USER_NAME_MAX_LEN,
    FIRST_NAME_MAX_LEN,
    LAST_NAME_MAX_LEN,
    EMAIL_MAX_LEN,
)

from .fam_user_type import FamUserTypeSchema


class FamUserInfoSchema(BaseModel):

    user_name: Annotated[str, StringConstraints(max_length=USER_NAME_MAX_LEN)]
    user_type_relation: FamUserTypeSchema = Field(alias="user_type")
    first_name: Optional[
        Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    ] = None
    last_name: Optional[
        Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    ] = None
    email: Optional[Annotated[str, StringConstraints(max_length=EMAIL_MAX_LEN)]] = None

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        from_attributes=True,
        fields={
            "user_guid": {"exclude": True},
            "create_user": {"exclude": True},
            "update_user": {"exclude": True},
        },
        populate_by_name=True,
    )
