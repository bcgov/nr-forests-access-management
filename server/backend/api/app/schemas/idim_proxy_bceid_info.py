from typing import Optional
from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated

from api.app.constants import (
    USER_NAME_MAX_LEN,
    FIRST_NAME_MAX_LEN,
    LAST_NAME_MAX_LEN,
    EMAIL_MAX_LEN,
)


class IdimProxyBceidInfoSchema(BaseModel):
    found: bool
    userId: Annotated[str, StringConstraints(max_length=USER_NAME_MAX_LEN)]
    guid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    businessGuid: Optional[Annotated[str, StringConstraints(max_length=32)]] = None
    businessLegalName: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    firstName: Optional[
        Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    ] = None
    lastName: Optional[
        Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    ] = None
    email: Optional[Annotated[str, StringConstraints(max_length=EMAIL_MAX_LEN)]] = None