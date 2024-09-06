from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated

from api.app.constants import USER_NAME_MAX_LEN


class IdimProxySearchParamSchema(BaseModel):
    userId: Annotated[
        str, StringConstraints(max_length=USER_NAME_MAX_LEN)
    ]  # param for Idim-Proxy search of this form (not snake case)
