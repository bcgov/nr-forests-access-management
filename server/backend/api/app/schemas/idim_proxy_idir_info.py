from typing import Optional
from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated


class IdimProxyIdirInfoSchema(BaseModel):
    # property returned from Idim-Proxy search of this form (not snake case)
    found: bool
    userId: Annotated[str, StringConstraints(max_length=20)]
    guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    firstName: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    lastName: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None
