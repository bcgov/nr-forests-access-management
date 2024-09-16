from typing import Optional

from pydantic import ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from .fam_forest_client import FamForestClientSchema
from .fam_role_min import FamRoleMinSchema


class FamRoleWithClientSchema(FamRoleMinSchema):
    role_id: int
    display_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    description: Optional[Annotated[str, StringConstraints(max_length=300)]] = Field(
        validation_alias="role_purpose"
    )
    forest_client: Optional[FamForestClientSchema] = None
    parent_role: Optional[FamRoleMinSchema] = None

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        from_attributes=True,
        fields={
            "update_user": {"exclude": True},
            "role_purpose": {"exclude": True},
            "parent_role_id": {"exclude": True},
            "application_id": {"exclude": True},
            "forest_client_number": {"exclude": True},
            "role_id": {"exclude": True},
            "create_user": {"exclude": True},
        },
    )
