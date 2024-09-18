import datetime
import logging
from http import HTTPStatus
from typing import List

from api.app.constants import (PrivilegeChangeTypeEnum,
                               PrivilegeDetailsPermissionTypeEnum,
                               PrivilegeDetailsScopeTypeEnum)
from api.app.models.model import FamUser
from api.app.repositories.permission_audit_repository import \
    PermissionAuditRepository
from api.app.schemas.fam_user_role_assignment_create_response import \
    FamUserRoleAssignmentCreateRes
from api.app.schemas.permission_audit_history import \
    PermissionAduitHistoryCreateSchema
from api.app.schemas.privilege_change_performer import \
    PrivilegeChangePerformerSchema
from api.app.schemas.privilege_details import (PrivilegeDetailsRoleSchema,
                                               PrivilegeDetailsSchema,
                                               PrivilegeDetailsScopeSchema)
from api.app.schemas.requester import RequesterSchema
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class PermissionAuditService:

    def __init__(self, db: Session):
        self.repo = PermissionAuditRepository(db)

    def store_user_permissions_granted_audit_history(
        self,
        requester: RequesterSchema,
        change_target_user: FamUser,
        new_user_permission_grated_list: List[FamUserRoleAssignmentCreateRes]
    ):
        success_granted_list = list(filter(
            lambda res: res.status_code == HTTPStatus.OK, new_user_permission_grated_list
        ))
        if (len(success_granted_list) == 0):
            LOGGER.debug("No success permission granted available. No audit record to store.")
            return

        audit_record = PermissionAduitHistoryCreateSchema(
            application_id=success_granted_list[0].detail.role.application.application_id,
            create_user=requester.user_name,
            change_performer_user_id=requester.user_id,
            change_target_user_id=change_target_user.user_id,
            change_performer_user_details=PermissionAuditService.to_change_performer_user_details(requester),
            privilege_change_type_code=PrivilegeChangeTypeEnum.GRANT,
            privilege_details=PermissionAuditService.to_enduser_privliege_details(success_granted_list),
            create_date=datetime.datetime.now(datetime.UTC),
            change_date=datetime.datetime.now(datetime.UTC)
        )
        LOGGER.debug(f"Adding audit record: {audit_record}")

        self.repo.save(audit_record)

    @staticmethod
    def to_change_performer_user_details(
        requester: RequesterSchema
    ) -> PrivilegeChangePerformerSchema:
        return PrivilegeChangePerformerSchema(
            username=requester.user_name,
            first_name=requester.first_name,
            last_name=requester.last_name,
            email=requester.email
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
