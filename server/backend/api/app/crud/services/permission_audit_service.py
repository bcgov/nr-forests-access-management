import datetime
import logging
from http import HTTPStatus
from typing import List

from api.app.constants import PrivilegeChangeTypeEnum
from api.app.models.model import FamUser
from api.app.repositories.permission_audit_repository import \
    PermissionAuditRepository
from api.app.schemas.fam_user_role_assignment_create_response import \
    FamUserRoleAssignmentCreateRes
from api.app.schemas.permission_audit_history import \
    PermissionAduitHistoryCreateSchema
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
            change_performer_user_details=PermissionAduitHistoryCreateSchema.to_change_performer_user_details(requester),
            privilege_change_type_code=PrivilegeChangeTypeEnum.GRANT,
            privilege_details=PermissionAduitHistoryCreateSchema.to_enduser_privliege_details(success_granted_list),
            create_date=datetime.datetime.now(datetime.UTC),
            change_date=datetime.datetime.now(datetime.UTC)
        )
        LOGGER.debug(f"Adding audit record: {audit_record}")

        self.repo.save(audit_record)
