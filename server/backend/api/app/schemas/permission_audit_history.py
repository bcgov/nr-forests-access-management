from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .privilege_details import PrivilegeDetailsSchema
from .privilege_change_performer import PrivilegeChangePerformerSchema


class PermissionAuditHistoryResDto(BaseModel):
    """
    This class is used to transfer data related to the changes made to a user's permissions,
    typically in the context of an audit trail. It encapsulates details about the change,
    including when it occurred, who performed the change, who the change was applied to,
    and the specific details of the permission changes.
    """

    change_date: datetime
    change_performer_user_details: PrivilegeChangePerformerSchema
    change_performer_user_id: Optional[int]
    create_date: datetime
    create_user: str
    privilege_change_type_code: str
    privilege_details: PrivilegeDetailsSchema

    model_config = ConfigDict(from_attributes=True)
