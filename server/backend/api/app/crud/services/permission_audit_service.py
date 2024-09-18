import datetime
import logging
from http import HTTPStatus
from typing import List

from api.app.constants import (ERROR_CODE_UNKNOWN_STATE,
                               PrivilegeChangeTypeEnum,
                               PrivilegeDetailsPermissionTypeEnum,
                               PrivilegeDetailsScopeTypeEnum)
from api.app.crud import crud_utils
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.models.model import FamUser, FamUserRoleXref
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
from fastapi import HTTPException
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
            privilege_details=PermissionAuditService.to_enduser_privliege_granted_details(success_granted_list),
            create_date=datetime.datetime.now(datetime.UTC),
            change_date=datetime.datetime.now(datetime.UTC)
        )

        LOGGER.debug(f"Adding audit record for ({PrivilegeChangeTypeEnum.GRANT}): {audit_record}")
        self.repo.save(audit_record)

    def store_user_permissions_revoked_audit_history(
        self, requester: RequesterSchema, delete_record: FamUserRoleXref
    ):
        revoked_permission_target_user = delete_record.user
        revoked_permission_role = delete_record.role
        audit_record = PermissionAduitHistoryCreateSchema(
            application_id=revoked_permission_role.application.application_id,
            create_user=requester.user_name,
            change_performer_user_id=requester.user_id,
            change_target_user_id=revoked_permission_target_user.user_id,
            change_performer_user_details=PermissionAuditService.to_change_performer_user_details(requester),
            privilege_change_type_code=PrivilegeChangeTypeEnum.REVOKE,
            privilege_details=PermissionAuditService.to_enduser_privliege_revoked_details(delete_record),
            create_date=datetime.datetime.now(datetime.UTC),
            change_date=datetime.datetime.now(datetime.UTC)
        )

        LOGGER.debug(f"Adding audit record for ({PrivilegeChangeTypeEnum.REVOKE}): {audit_record}")
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
    def to_enduser_privliege_granted_details(enduser_privliege_list: List[FamUserRoleAssignmentCreateRes]):
        if (len(enduser_privliege_list) == 0):
            return

        # Note, current FAM supports create ONLY 1 role with multiple forest_client(s) at ONLY 1 scope type ("CLIENT").
        # TODO !! When team begins new scoped roles model, it needs refactoring.  # noqa NOSONAR
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

    @staticmethod
    def to_enduser_privliege_revoked_details(delete_record: FamUserRoleXref):
        # Note, current FAM supports delet ONLY 1 role with ONLY 1 scope type ("CLIENT").
        # TODO !! When team begins new scoped roles model, it needs refactoring.  # noqa NOSONAR
        revoked_permission_role = delete_record.role
        is_forest_client_scoped_role = revoked_permission_role.client_number_id
        forest_client_number = None
        forest_client_name = None
        if (is_forest_client_scoped_role):
            forest_client_number = revoked_permission_role.client_number.forest_client_number
            api_instance_env = crud_utils.use_api_instance_by_app(revoked_permission_role.application)
            forest_client_integration_service = ForestClientIntegrationService(api_instance_env)
            fc_search_result = forest_client_integration_service.find_by_client_number(
                forest_client_number
            )
            # Search forest client name for storing audit record.
            # Forest Client search is an exact search.
            if len(fc_search_result) == 1:
                forest_client_name = fc_search_result[0]["clientName"]
            else:
                error_msg = (
                    "Revoke user permission encountered problem."
                    + f"Unknown forest client number {forest_client_number} for "
                    + "scoped permission {revoked_permission_role.role_name}."
                )
                LOGGER.debug(error_msg)
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail={
                        "code": ERROR_CODE_UNKNOWN_STATE,
                        "description": error_msg
                    }
                )

        revoke_privilege_details_scope = PrivilegeDetailsScopeSchema(
            scope_type=PrivilegeDetailsScopeTypeEnum.CLIENT,
            client_id=forest_client_number if is_forest_client_scoped_role else None,
            client_name=forest_client_name if is_forest_client_scoped_role else None
        )
        role = PrivilegeDetailsRoleSchema(
            role=revoked_permission_role.display_name,
            scopes=[revoke_privilege_details_scope]
        )

        return PrivilegeDetailsSchema(
            permission_type=PrivilegeDetailsPermissionTypeEnum.END_USER,
            roles=[role]
        )
