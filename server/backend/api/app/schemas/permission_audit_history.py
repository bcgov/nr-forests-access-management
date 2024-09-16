from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .privilege_change_performer import PrivilegeChangePerformerSchema
from .privilege_details import PrivilegeDetailsSchema


class PermissionAduitHistoryBaseSchema(BaseModel):
    """
    This is a base DTO class for "Privliege Change Audit".
    """
    create_date: datetime
    create_user: str
    change_date: datetime
    change_performer_user_details: PrivilegeChangePerformerSchema
    privilege_change_type_code: str
    privilege_details: PrivilegeDetailsSchema

    model_config = ConfigDict(from_attributes=True)


class PermissionAduitHistoryCreateSchema(PermissionAduitHistoryBaseSchema):
    """
    This is the class for "create" of a "Privliege Change Audit" record.
    """
    application_id: int
    change_performer_user_id: int
    change_target_user_id: int


class PermissionAduitHistoryRes(PermissionAduitHistoryBaseSchema):
    """
    This class is used to transfer data related to the changes made to a user's permissions,
    typically in the context of an audit trail. It encapsulates details about the change,
    including when it occurred, who performed the change, who the change was applied to,
    and the specific details of the permission changes.
    """
    privilege_change_audit_id: int
    change_performer_user_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)
