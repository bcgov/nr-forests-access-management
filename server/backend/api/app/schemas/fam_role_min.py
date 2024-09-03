from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated
from api.app.constants import RoleType
from .fam_application import FamApplicationSchema


class FamRoleMinSchema(BaseModel):
    role_name: Annotated[str, StringConstraints(max_length=100)]
    role_type_code: RoleType
    application: FamApplicationSchema

    model_config = ConfigDict(from_attributes=True)
