from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated


class IdimProxySearchParamSchema(BaseModel):
    userId: Annotated[
        str, StringConstraints(max_length=20)
    ]  # param for Idim-Proxy search of this form (not snake case)
