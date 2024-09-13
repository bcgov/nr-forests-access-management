from typing import Optional
from pydantic import StringConstraints
from typing_extensions import Annotated

from api.app.constants import FIRST_NAME_MAX_LEN, LAST_NAME_MAX_LEN, EMAIL_MAX_LEN

from .requester import RequesterSchema


class TargetUserSchema(RequesterSchema):
    """
    Inherit from the class "Requester". Same as Requester, the TargetUser can
    be transformed from FamUser db model.
    """

    user_id: Optional[int] = None
    first_name: Optional[
        Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    ] = None
    last_name: Optional[
        Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    ] = None
    email: Optional[Annotated[str, StringConstraints(max_length=EMAIL_MAX_LEN)]] = None
