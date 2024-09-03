from pydantic import BaseModel
from api.app.constants import IdimSearchUserParamType


class IdimProxyBceidSearchParamSchema(BaseModel):
    searchUserBy: IdimSearchUserParamType
    searchValue: str
