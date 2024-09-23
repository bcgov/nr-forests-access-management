from typing import List, Optional

from api.app.constants import (CLIENT_NAME_MAX_LEN, CLIENT_NUMBER_MAX_LEN,
                               ROLE_NAME_MAX_LEN,
                               PrivilegeDetailsPermissionTypeEnum,
                               PrivilegeDetailsScopeTypeEnum)
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator
from typing_extensions import Annotated


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
    scopes: Optional[List[PrivilegeDetailsScopeSchema]] = None


class PrivilegeDetailsSchema(BaseModel):
    """
    This schema represents the structure of the `privilege_details` JSON field used in the `fam_privilege_change_audit` table.

    The `privilege_details` field captures the details of the privileges being changed during a privilege audit event.
    It includes information about the `permission_type` and, types of permissions, the associated roles and scopes.

    Attributes:
        permission_type (PrivilegeDetailsPermissionTypeEnum): The type of permission being changed.
        roles (List[PrivilegeDetailsRoleSchema], optional): A list of roles associated with the permission.
              Required for `END_USER` and `DELEGATED_ADMIN` permission types, and should be omitted for `APPLICATION_ADMIN`.

    Validation:
        The schema includes a validator to ensure that roles are appropriately present or absent based on the `permission_type`.
    """

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
