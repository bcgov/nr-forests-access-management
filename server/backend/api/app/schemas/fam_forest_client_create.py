from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated


# --------------------------------- FAM Forest Client--------------------------------- #
class FamForestClientCreateSchema(BaseModel):
    # Note, the request may contain string(with leading '0')
    forest_client_number: Annotated[str, StringConstraints(max_length=8)]
    # client_name: str
    create_user: Annotated[str, StringConstraints(max_length=100)]

    model_config = ConfigDict(from_attributes=True)
