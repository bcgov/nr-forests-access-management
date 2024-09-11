from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .privilege_details import PrivilegeDetailsSchema
from .privilege_change_performer import (
    PrivilegeChangePerformerSchema,
)


class PermissionAuditHistoryResDto(BaseModel):
    """
    This class is used to transfer data related to the changes made to a user's permissions,
    typically in the context of an audit trail. It encapsulates details about the change,
    including when it occurred, who performed the change, who the change was applied to,
    and the specific details of the permission changes.

    Attributes:
        change_date (datetime): The date and time when the permission change occurred.
        change_performer_user_details (PrivilegeChangePerformerSchema): Details of the user
            or system that performed the permission change, including relevant user information.
        change_performer_user_id (Optional[int]): The ID of the user who performed the change.
            This may be `None` if the change was performed by the system or if the user ID is unavailable.
        create_date (datetime): The date and time when this record was created in the system.
        create_user (str): The username or identifier of the entity that created this change record.
        privilege_change_type_code (str): The code representing the type of permission change,
            such as adding or removing a specific role or scope.
        privilege_details (PrivilegeDetailsSchema): The details of the permission change,
            including information about the roles and scopes that were added, removed, or modified.

    This DTO is designed to be used in API responses where partial data from the
    `FamPrivilegeChangeAudit` model needs to be exposed. It ensures that only the relevant
    fields are included in the response.
    """

    change_date: datetime
    change_performer_user_details: PrivilegeChangePerformerSchema
    change_performer_user_id: Optional[int]
    create_date: datetime
    create_user: str
    privilege_change_type_code: str
    privilege_details: PrivilegeDetailsSchema

    class Config:
        orm_mode = True
