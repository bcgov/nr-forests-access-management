from typing import Optional
from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated


class IdimProxyBceidInfoSchema(BaseModel):
    found: bool
    userId: Annotated[str, StringConstraints(max_length=20)]
    guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    businessGuid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    businessLegalName: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    firstName: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    lastName: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None
