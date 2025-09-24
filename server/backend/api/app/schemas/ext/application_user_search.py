from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field


class ApplicationUserSearchSchema(BaseModel):
    idp_type: Optional[str] = Field(Query(default=None), alias="idpType")
    idp_username: Optional[str] = Field(Query(default=None), alias="idpUsername")
    first_name: Optional[str] = Field(Query(default=None), alias="firstName")
    last_name: Optional[str] = Field(Query(default=None), alias="lastName")
    role: Optional[List[str]] = Field(Query(default=None), alias="role")

    model_config = ConfigDict(from_attributes=True)
