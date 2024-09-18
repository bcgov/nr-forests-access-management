from typing import Optional

from pydantic import ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from .fam_forest_client import FamForestClientSchema
from .fam_role_min import FamRoleMinSchema


class FamRoleWithClientSchema(FamRoleMinSchema):
    role_id: int
    display_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    description: Optional[Annotated[str, StringConstraints(max_length=300)]] = Field(
        alias="role_purpose"
    )
    forest_client: Optional[FamForestClientSchema] = Field(
        alias="client_number"
    )
    parent_role: Optional[FamRoleMinSchema] = None

    model_config = ConfigDict(from_attributes=True)
