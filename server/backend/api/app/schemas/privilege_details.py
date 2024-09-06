from typing import List, Optional
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator
from typing_extensions import Annotated, Literal


class ScopeSchema(BaseModel):
    scope_type: Literal["Client", "District"]
    client_id: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    client_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    district_id: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    district_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None


class RoleSchema(BaseModel):
    role: Annotated[str, StringConstraints(max_length=50)]
    scopes: List[ScopeSchema]


class PrivilegeDetailsSchema(BaseModel):
    permission_type: Literal["End User", "Delegated Admin", "Application Admin"]
    roles: Optional[List[RoleSchema]] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def check_roles_based_on_permission_type(cls, values):
        permission_type = values.get("permission_type")
        roles = values.get("roles")

        if permission_type == "Application Admin" and roles is not None:
            raise ValueError(
                "roles should not be present when permission_type is Application Admin"
            )
        elif permission_type in {"End User", "Delegated Admin"} and roles is None:
            raise ValueError(
                "roles are required when permission_type is End User or Delegated Admin"
            )

        return values
