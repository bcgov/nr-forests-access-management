import logging
from http import HTTPStatus
from typing import List

from api.app import constants as famConstants
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.integration.gc_notify import GCNotifyEmailService
from api.app.repositories.access_control_privilege_repository import \
    AccessControlPrivilegeRepository
from api.app.schemas.pagination import (DelegatedAdminPageParamsSchema,
                                        PagedResultsSchema)
from api.app.schemas.schemas import (FamAccessControlPrivilegeCreateDto,
                                     FamAccessControlPrivilegeCreateRequest,
                                     FamAccessControlPrivilegeCreateResponse,
                                     FamAccessControlPrivilegeGetResponse,
                                     FamForestClientBase,
                                     GCNotifyGrantDelegatedAdminEmailParam,
                                     Requester, TargetUser)
from api.app.services import utils_service
from api.app.services.permission_audit_service import PermissionAuditService
from api.app.services.role_service import RoleService
from api.app.services.user_service import UserService
from api.app.services.validator.forest_client_validator import (
    forest_client_active, forest_client_number_exists,
    get_forest_client_status)
from api.app.utils import utils
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class AccessControlPrivilegeService:
    def __init__(self, db: Session):
        self.user_service = UserService(db)
        self.role_service = RoleService(db)
        self.permission_audit_service = PermissionAuditService(db)
        self.access_control_privilege_repository = AccessControlPrivilegeRepository(db)

    def get_paged_delegated_admin_assignment_by_application_id(
        self, application_id: int, page_params: DelegatedAdminPageParamsSchema
    ) -> PagedResultsSchema[FamAccessControlPrivilegeGetResponse]:
        """
        Service method to get access control privilege (a.k.a Delegated Admin) by application id.
        Arguments:
            application_id (int): The application's id, to find out the delegated admins
            belong to this application.

            page_params (DelegatedAdminPageParamsSchema): pagination parameters for query to
            return paged results.

        Returns:
            PagedResultsSchema[FamAccessControlPrivilegeGetResponse]: A paged results containing
            pagination metadata and a list of delegated admins assigned to this application.
        """
        return self.access_control_privilege_repository.get_paged_delegated_admins_assignment_by_application_id(
            application_id=application_id, page_params=page_params
        )

    def get_acp_by_user_id_and_role_id(self, user_id: int, role_id: int):
        return self.access_control_privilege_repository.get_acp_by_user_id_and_role_id(
            user_id, role_id
        )

    def get_acp_by_id(self, access_control_privilege_id: int):
        return self.access_control_privilege_repository.get_acp_by_id(
            access_control_privilege_id
        )

    def get_acp_by_application_id(
        self, application_id: int
    ) -> List[FamAccessControlPrivilegeGetResponse]:
        return self.access_control_privilege_repository.get_acp_by_application_id(
            application_id
        )

    def delete_access_control_privilege(self, requester: Requester, access_control_privilege_id: int):
        deleted_record = self.access_control_privilege_repository.delete_access_control_privilege(
            access_control_privilege_id
        )
        # save audit record
        self.permission_audit_service.store_delegated_admin_permissions_revoked_audit_history(
            requester, deleted_record
        )

    def create_access_control_privilege_many(
        self,
        request: FamAccessControlPrivilegeCreateRequest,
        requester: Requester,
        target_user: TargetUser,
    ) -> List[FamAccessControlPrivilegeCreateResponse]:
        LOGGER.debug(
            f"Request for assigning access role privilege to a user: {request}."
        )

        # Verify if user already exists or add a new user
        fam_user = self.user_service.find_or_create(
            request.user_type_code, request.user_name, request.user_guid, requester.cognito_user_id
        )
        fam_user = self.user_service.update_user_properties_from_verified_target_user(
            fam_user.user_id, target_user, requester.cognito_user_id
        )

        # Verify if role exists
        fam_role = self.role_service.get_role_by_id(request.role_id)
        if not fam_role:
            error_msg = f"Role id {request.role_id} does not exist."
            utils.raise_http_exception(
                error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                error_msg=error_msg,
            )

        # Role is a 'Abstract' type, create access control privilege with forst client child role
        require_child_role = (
            fam_role.role_type_code == famConstants.RoleType.ROLE_TYPE_ABSTRACT
        )

        new_delegated_admin_permission_granted_list: List[FamAccessControlPrivilegeCreateResponse] = []

        if require_child_role:
            LOGGER.debug(
                f"Role {fam_role.role_name} requires child role "
                "for creating delegate admin access control privilege."
            )

            if (
                not hasattr(request, "forest_client_numbers")
                or request.forest_client_numbers is None
                or len(request.forest_client_numbers) < 1
            ):
                error_msg = "Invalid access control privilege request, missing forest client number."
                utils.raise_http_exception(
                    error_code=famConstants.ERROR_CODE_MISSING_KEY_ATTRIBUTE,
                    error_msg=error_msg,
                )

            forest_client_integration_service = ForestClientIntegrationService(
                utils_service.use_api_instance_by_app_env(
                    fam_role.application.app_environment
                )
            )
            for forest_client_number in request.forest_client_numbers:
                # validate the forest client number
                forest_client_search_return = forest_client_integration_service.find_by_client_number(
                    forest_client_number
                )
                if not forest_client_number_exists(forest_client_search_return):
                    error_msg = (
                        "Invalid access control privilege request. "
                        + f"Forest client number {forest_client_number} does not exist."
                    )
                    utils.raise_http_exception(
                        error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                        error_msg=error_msg,
                    )

                if not forest_client_active(forest_client_search_return):
                    error_msg = (
                        "Invalid access control privilege request. "
                        + f"Forest client number {forest_client_number} is not in active status: "
                        + f"{get_forest_client_status(forest_client_search_return)}."
                    )
                    utils.raise_http_exception(
                        error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                        error_msg=error_msg,
                    )

                # Check if child role exists or add a new child role
                child_role = self.role_service.find_or_create_forest_client_child_role(
                    forest_client_number, fam_role, requester.cognito_user_id
                )
                new_delegated_admin_grant_res = self.grant_privilege(
                    fam_user.user_id, child_role.role_id, requester.cognito_user_id
                )
                # Update response object for Forest Client Name from the forest_client_search.
                # FAM currently does not store forest client name for easy retrieval.
                new_delegated_admin_grant_res.detail.role.forest_client = (
                    FamForestClientBase.from_api_json(forest_client_search_return[0])
                )
                new_delegated_admin_permission_granted_list.append(new_delegated_admin_grant_res)
        else:
            new_delegated_admin_grant_res = self.grant_privilege(
                fam_user.user_id, fam_role.role_id, requester.cognito_user_id
            )
            new_delegated_admin_permission_granted_list.append(new_delegated_admin_grant_res)

        LOGGER.debug(
            f"Creating access control privilege executed successfully: {new_delegated_admin_permission_granted_list}"
        )

        self.permission_audit_service.store_delegated_admin_permissions_granted_audit_history(
            requester, fam_user, new_delegated_admin_permission_granted_list
        )

        return new_delegated_admin_permission_granted_list

    def grant_privilege(
        self, user_id: int, role_id: int, requester_cognito_user_id: str
    ) -> FamAccessControlPrivilegeCreateResponse:
        access_control_privilege_return = None

        # Check if user privilege already exists
        fam_access_control_privilege = self.get_acp_by_user_id_and_role_id(
            user_id, role_id
        )

        if fam_access_control_privilege:
            error_msg = (
                "User already has the requested access control privilege for "
                + f"{fam_access_control_privilege.role.role_name}"
            )

            LOGGER.debug(
                f"{error_msg}"
                + "with id: "
                + f"{fam_access_control_privilege.access_control_privilege_id}."
            )

            fam_access_control_privilege_dict = fam_access_control_privilege.__dict__
            access_control_privilege_return = (
                FamAccessControlPrivilegeCreateResponse(
                    **{
                        "status_code": HTTPStatus.CONFLICT,
                        "detail": FamAccessControlPrivilegeGetResponse(
                            **fam_access_control_privilege_dict
                        ),
                        "error_message": error_msg,
                    }
                )
            )
        else:
            access_control_privilege_param = FamAccessControlPrivilegeCreateDto(
                **{
                    "user_id": user_id,
                    "role_id": role_id,
                    "create_user": requester_cognito_user_id,
                }
            )
            fam_access_control_privilege = self.access_control_privilege_repository.create_access_control_privilege(
                access_control_privilege_param
            )
            fam_access_control_privilege_dict = fam_access_control_privilege.__dict__
            access_control_privilege_return = (
                FamAccessControlPrivilegeCreateResponse(
                    **{
                        "status_code": HTTPStatus.OK,
                        "detail": FamAccessControlPrivilegeGetResponse(
                            **fam_access_control_privilege_dict
                        ),
                    }
                )
            )

        return access_control_privilege_return

    def send_email_notification(
        self,
        target_user: TargetUser,
        access_control_priviliege_response: List[FamAccessControlPrivilegeCreateResponse],
    ):
        try:
            granted_roles_res = list(filter(
                lambda res: res.status_code == HTTPStatus.OK,
                access_control_priviliege_response,
            ))

            if len(granted_roles_res) == 0:  # no role is granted
                return

            gc_notify_email_service = GCNotifyEmailService()
            is_bceid_user = "yes" if target_user.user_type_code == famConstants.UserType.BCEID else "no"
            granted_role = access_control_priviliege_response[0].detail.role
            is_forest_client_scoped_role = granted_role.forest_client is not None
            granted_role_client_list = (
                list(map(lambda item: item.detail.role.forest_client, granted_roles_res))
                if is_forest_client_scoped_role
                else None
            )
            email_response = gc_notify_email_service.send_delegated_admin_granted_email(
                GCNotifyGrantDelegatedAdminEmailParam(
                    ** {
                        "send_to_email_address": target_user.email,
                        "application_description": granted_role.application.application_description,
                        "role_display_name": granted_role.display_name,
                        "organization_list": granted_role_client_list,
                        "user_name": target_user.user_name,
                        "first_name": target_user.first_name,
                        "last_name": target_user.last_name,
                        "is_bceid_user": is_bceid_user
                    }
                )
            )
            LOGGER.debug(f"Email is sent to {target_user.email}: {email_response}")
            return famConstants.EmailSendingStatus.SENT_TO_EMAIL_SERVICE_SUCCESS
        except Exception as e:
            LOGGER.debug(
                f"Failure sending email to the new delegated admin {target_user.email}."
            )
            LOGGER.debug(f"Failure reason : {e}.")
            return famConstants.EmailSendingStatus.SENT_TO_EMAIL_SERVICE_FAILURE