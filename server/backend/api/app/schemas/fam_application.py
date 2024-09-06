from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated


class FamApplicationSchema(BaseModel):
    application_id: int
    application_name: Annotated[str, StringConstraints(max_length=100)]
    application_description: Annotated[str, StringConstraints(max_length=200)]

    model_config = ConfigDict(from_attributes=True)
