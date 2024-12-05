from typing import Optional, Union

from api.app.constants import ROLE_NAME_MAX_LEN, RoleType
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from .fam_forest_client_create import FamForestClientCreateSchema


class FamRoleCreateSchema(BaseModel):
    role_name: Annotated[str, StringConstraints(max_length=ROLE_NAME_MAX_LEN)]
    role_purpose: Union[Annotated[str, StringConstraints(max_length=300)], None] = None
    display_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    parent_role_id: Union[int, None] = Field(
        default=None, title="Reference role_id to higher role"
    )
    application_id: int = Field(title="Application this role is associated with")
    role_type_code: RoleType
    forest_client_number: Union[
        Annotated[str, StringConstraints(max_length=8)], None
    ] = Field(default=None, title="Forest Client this role is associated with")
    create_user: Annotated[str, StringConstraints(max_length=100)]

    model_config = ConfigDict(from_attributes=True)
