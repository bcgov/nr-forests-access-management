from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated
from .fam_user_type import FamUserTypeSchema


class FamUserInfoSchema(BaseModel):

    user_name: Annotated[str, StringConstraints(max_length=20)]
    user_type_relation: FamUserTypeSchema = Field(alias="user_type")
    first_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None

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
