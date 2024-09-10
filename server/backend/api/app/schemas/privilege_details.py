from typing import List, Optional
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator
from typing_extensions import Annotated

from api.app.constants import (
    CLIENT_NUMBER_MAX_LEN,
    CLIENT_NAME_MAX_LEN,
    ROLE_NAME_MAX_LEN,
    PrivilegeDetailsScopeTypeEnum,
    PrivilegeDetailsPermissionTypeEnum,
)


class PrivilegeDetailsScopeSchema(BaseModel):
    scope_type: PrivilegeDetailsScopeTypeEnum
    client_id: Optional[
        Annotated[str, StringConstraints(max_length=CLIENT_NUMBER_MAX_LEN)]
    ] = None
    client_name: Optional[
        Annotated[str, StringConstraints(max_length=CLIENT_NAME_MAX_LEN)]
    ] = None


class PrivilegeDetailsRoleSchema(BaseModel):
    role: Annotated[str, StringConstraints(max_length=ROLE_NAME_MAX_LEN)]
    scopes: List[PrivilegeDetailsScopeSchema]


class PrivilegeDetailsSchema(BaseModel):
    permission_type: PrivilegeDetailsPermissionTypeEnum
    roles: Optional[List[PrivilegeDetailsRoleSchema]] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def check_roles_based_on_permission_type(cls, values):
        permission_type = values.get("permission_type")
        roles = values.get("roles")

        if (
            permission_type == PrivilegeDetailsPermissionTypeEnum.APPLICATION_ADMIN
            and roles is not None
        ):
            raise ValueError(
                "roles should not be present when permission_type is Application Admin"
            )
        elif (
            permission_type
            in {
                PrivilegeDetailsPermissionTypeEnum.END_USER,
                PrivilegeDetailsPermissionTypeEnum.DELEGATED_ADMIN,
            }
            and roles is None
        ):
            raise ValueError(
                "roles are required when permission_type is End User or Delegated Admin"
            )

        return values
