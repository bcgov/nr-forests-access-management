from api.app.constants import UserType
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


class FamUserTypeSchema(BaseModel):
    user_type_code: UserType = Field(alias="code")
    description: Annotated[str, StringConstraints(max_length=35)]

    # required to set populate_by_name for alias fields
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
