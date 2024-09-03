from typing import Optional
from pydantic import StringConstraints
from typing_extensions import Annotated

from .requester import RequesterSchema


class TargetUserSchema(RequesterSchema):
    """
    Inherit from the class "Requester". Same as Requester, the TargetUser can
    be transformed from FamUser db model.
    """

    user_id: Optional[int] = None
    first_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[Annotated[str, StringConstraints(max_length=250)]] = None
