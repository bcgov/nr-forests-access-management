from api.app.constants import (APPLICATION_DESC_MAX_LEN,
                               APPLICATION_NAME_MAX_LEN)
from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated


class FamApplicationSchema(BaseModel):
    application_id: int
    application_name: Annotated[str, StringConstraints(max_length=APPLICATION_NAME_MAX_LEN)]
    application_description: Annotated[str, StringConstraints(max_length=APPLICATION_DESC_MAX_LEN)]

    model_config = ConfigDict(from_attributes=True)
