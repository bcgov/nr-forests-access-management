from datetime import datetime
from typing import List, Optional

from api.app.constants import (CLIENT_NAME_MAX_LEN, CLIENT_NUMBER_MAX_LEN,
                               EMAIL_MAX_LEN, FIRST_NAME_MAX_LEN,
                               LAST_NAME_MAX_LEN, ROLE_NAME_MAX_LEN,
                               SYSTEM_ACCOUNT_NAME, USER_NAME_MAX_LEN,
                               PrivilegeDetailsPermissionTypeEnum,
                               PrivilegeDetailsScopeTypeEnum)
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator
from typing_extensions import Annotated

"""
Schemas classes for business domain "Permission Audit History" related.
"""

class PermissionAduitHistoryBaseSchema(BaseModel):
    """
    This is a base DTO class for "Privliege Change Audit".
    """
    create_date: datetime
    create_user: str
    change_date: datetime
    change_performer_user_details: 'PrivilegeChangePerformerSchema'
    privilege_change_type_code: str
    privilege_details: 'PrivilegeDetailsSchema'

    model_config = ConfigDict(from_attributes=True)

class PermissionAduitHistoryCreateSchema(PermissionAduitHistoryBaseSchema):
    """
    This is the class for "create" of a "Privliege Change Audit" record.
    """
    application_id: int
    change_performer_user_id: int
    change_target_user_id: int

class PrivilegeChangePerformerSchema(BaseModel):
    """
    This schema represents the structure of the `change_user_details` JSON field used in fam_privilege_change_audit.

    The `change_user_details` field captures information about the user who performed a change, including
    the `username`, `first_name`, `last_name`, and `email`. It is used to record the user details at the time
    of the audit event, ensuring that changes to these details later do not affect the integrity of the audit log.

    For regular users, all fields (`username`, `first_name`, `last_name`, and `email`) are included. However,
    when the change is performed by a system account, only the `username` field is present, and it is set to
    "system". The schema includes validation logic to enforce this rule.

    Attributes:
        username (str): The username of the user performing the change. For system accounts, this is "system".
        first_name (str, optional): The first name of the user. Not present for system accounts.
        last_name (str, optional): The last name of the user. Not present for system accounts.
        email (str, optional): The email address of the user. Not present for system accounts.

    Validation:
        The schema includes a validator to ensure that for system accounts (where `username` is "system"),
        no other fields (`first_name`, `last_name`, `email`) are populated.
    """

    username: Annotated[str, StringConstraints(max_length=USER_NAME_MAX_LEN)]
    first_name: Optional[
        Annotated[str, StringConstraints(max_length=FIRST_NAME_MAX_LEN)]
    ] = None
    last_name: Optional[
        Annotated[str, StringConstraints(max_length=LAST_NAME_MAX_LEN)]
    ] = None
    email: Optional[Annotated[str, StringConstraints(max_length=EMAIL_MAX_LEN)]] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def validate_user_details(cls, values):
        username = values.get("username")
        first_name = values.get("first_name")
        last_name = values.get("last_name")
        email = values.get("email")

        if username == SYSTEM_ACCOUNT_NAME:
            # For system accounts, only username should be present
            if first_name or last_name or email:
                raise ValueError("System account should only have a username.")
        # For regular users, no additional checks are needed; username is the only required field.

        return values

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
    roles: Optional[List['PrivilegeDetailsRoleSchema']] = None

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


# ---------------------------- Request and Response ---------------------------- #

class PermissionAduitHistoryRes(PermissionAduitHistoryBaseSchema):
    """
    This class is used to transfer data related to the changes made to a user's permissions,
    typically in the context of an audit trail. It encapsulates details about the change,
    including when it occurred, who performed the change, who the change was applied to,
    and the specific details of the permission changes.
    """
    privilege_change_audit_id: int
    change_performer_user_id: Optional[int]
    privilege_change_type_description: str

    model_config = ConfigDict(from_attributes=True)