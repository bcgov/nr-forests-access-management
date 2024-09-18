from datetime import datetime
from typing import List, Optional

from api.app.constants import (PrivilegeDetailsPermissionTypeEnum,
                               PrivilegeDetailsScopeTypeEnum)
from api.app.schemas.fam_user_role_assignment_create_response import \
    FamUserRoleAssignmentCreateRes
from api.app.schemas.requester import RequesterSchema
from pydantic import BaseModel, ConfigDict

from .privilege_change_performer import PrivilegeChangePerformerSchema
from .privilege_details import (PrivilegeDetailsRoleSchema,
                                PrivilegeDetailsSchema,
                                PrivilegeDetailsScopeSchema)


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


class PermissionAduitHistoryCreateSchema(PermissionAduitHistoryBaseSchema):
    """
    This is the class for "create" of a "Privliege Change Audit" record.
    """
    application_id: int
    change_performer_user_id: int
    change_target_user_id: int

    @staticmethod
    def to_change_performer_user_details(
        requester: RequesterSchema
    ) -> PrivilegeChangePerformerSchema:
        return PrivilegeChangePerformerSchema(
            **requester.model_dump()
        )

    @staticmethod
    def to_enduser_privliege_details(enduser_privliege_list: List[FamUserRoleAssignmentCreateRes]):
        if (len(enduser_privliege_list) == 0):
            return

        # Note, current FAM supports create ONLY 1 role with multiple forest_client(s) at ONLY 1 scope type ("CLIENT").
        # TODO !! When team begins new scoped role model, it needs refactored.  # noqa NOSONAR
        def __map_to_privilege_role_scope(item: FamUserRoleAssignmentCreateRes):
            assigned_role = item.detail.role
            is_forest_client_scoped_role = assigned_role.forest_client is not None
            return PrivilegeDetailsScopeSchema(
                scope_type=PrivilegeDetailsScopeTypeEnum.CLIENT,
                client_id=assigned_role.forest_client.forest_client_number if is_forest_client_scoped_role else None,
                client_name=assigned_role.forest_client.client_name if is_forest_client_scoped_role else None
            )

        scopes = list(map(__map_to_privilege_role_scope, enduser_privliege_list))
        role = PrivilegeDetailsRoleSchema(
            role=enduser_privliege_list[0].detail.role.display_name,
            scopes=scopes
        )

        return PrivilegeDetailsSchema(
            permission_type=PrivilegeDetailsPermissionTypeEnum.END_USER,
            roles=[role]
        )
