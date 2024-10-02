from api.app.constants import CLIENT_NUMBER_MAX_LEN, CREATE_USER_MAX_LEN
from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated


# --------------------------------- FAM Forest Client--------------------------------- #
class FamForestClientCreateSchema(BaseModel):
    # Note, the request may contain string(with leading '0')
    forest_client_number: Annotated[str, StringConstraints(max_length=CLIENT_NUMBER_MAX_LEN)]

    create_user: Annotated[str, StringConstraints(max_length=CREATE_USER_MAX_LEN)]

    model_config = ConfigDict(from_attributes=True)
