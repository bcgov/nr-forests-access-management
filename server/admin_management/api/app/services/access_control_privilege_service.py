import logging
from http import HTTPStatus
from typing import List

from api.app import constants as famConstants
from api.app import schemas
from api.app.integration.forest_client_integration import ForestClientIntegrationService
from api.app.integration.gc_notify import GCNotifyEmailService
from api.app.repositories.access_control_privilege_repository import (
    AccessControlPrivilegeRepository,
)
from api.app.services import utils_service
from api.app.services.role_service import RoleService
from api.app.services.user_service import UserService
from api.app.services.validator.forest_client_validator import (
    forest_client_active,
    forest_client_number_exists,
    get_forest_client_status,
)
from api.app.utils import utils
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class AccessControlPrivilegeService:
    def __init__(self, db: Session):
        self.user_service = UserService(db)
        self.role_service = RoleService(db)
        self.access_control_privilege_repository = AccessControlPrivilegeRepository(db)

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
    ) -> List[schemas.FamAccessControlPrivilegeGetResponse]:
        return self.access_control_privilege_repository.get_acp_by_application_id(
            application_id
        )

    def delete_access_control_privilege(self, access_control_privilege_id: int):
        return self.access_control_privilege_repository.delete_access_control_privilege(
            access_control_privilege_id
        )

    def create_access_control_privilege_many(
        self,
        request: schemas.FamAccessControlPrivilegeCreateRequest,
        requester: str,
        target_user: schemas.TargetUser,
    ) -> List[schemas.FamAccessControlPrivilegeCreateResponse]:
        LOGGER.debug(
            f"Request for assigning access role privilege to a user: {request}."
        )

        # Verify if user already exists or add a new user
        fam_user = self.user_service.find_or_create(
            request.user_type_code, request.user_name, request.user_guid, requester
        )
        fam_user = self.user_service.update_user_properties_from_verified_target_user(
            fam_user.user_id, target_user, requester
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

        create_return_list: List[schemas.FamAccessControlPrivilegeCreateResponse] = []

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
                forest_client_validator_return = (
                    forest_client_integration_service.find_by_client_number(
                        forest_client_number
                    )
                )
                if not forest_client_number_exists(forest_client_validator_return):
                    error_msg = (
                        "Invalid access control privilege request. "
                        + f"Forest client number {forest_client_number} does not exist."
                    )
                    utils.raise_http_exception(
                        error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                        error_msg=error_msg,
                    )

                if not forest_client_active(forest_client_validator_return):
                    error_msg = (
                        "Invalid access control privilege request. "
                        + f"Forest client number {forest_client_number} is not in active status: "
                        + f"{get_forest_client_status(forest_client_validator_return)}."
                    )
                    utils.raise_http_exception(
                        error_code=famConstants.ERROR_CODE_INVALID_REQUEST_PARAMETER,
                        error_msg=error_msg,
                    )

                # Check if child role exists or add a new child role
                child_role = self.role_service.find_or_create_forest_client_child_role(
                    forest_client_number, fam_role, requester
                )
                handle_create_return = self.grant_privilege(
                    fam_user.user_id, child_role.role_id, requester
                )
                create_return_list.append(handle_create_return)
        else:
            handle_create_return = self.grant_privilege(
                fam_user.user_id, fam_role.role_id, requester
            )
            create_return_list.append(handle_create_return)

        LOGGER.debug(
            f"Creating access control privilege executed successfully: {create_return_list}"
        )

        return create_return_list

    def grant_privilege(
        self, user_id: int, role_id: int, requester: str
    ) -> schemas.FamAccessControlPrivilegeCreateResponse:
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
                schemas.FamAccessControlPrivilegeCreateResponse(
                    **{
                        "status_code": HTTPStatus.CONFLICT,
                        "detail": schemas.FamAccessControlPrivilegeGetResponse(
                            **fam_access_control_privilege_dict
                        ),
                        "error_message": error_msg,
                    }
                )
            )
        else:
            access_control_privilege_param = schemas.FamAccessControlPrivilegeCreateDto(
                **{
                    "user_id": user_id,
                    "role_id": role_id,
                    "create_user": requester,
                }
            )
            fam_access_control_privilege = self.access_control_privilege_repository.create_access_control_privilege(
                access_control_privilege_param
            )
            fam_access_control_privilege_dict = fam_access_control_privilege.__dict__
            access_control_privilege_return = (
                schemas.FamAccessControlPrivilegeCreateResponse(
                    **{
                        "status_code": HTTPStatus.OK,
                        "detail": schemas.FamAccessControlPrivilegeGetResponse(
                            **fam_access_control_privilege_dict
                        ),
                    }
                )
            )

        return access_control_privilege_return

    def send_email_notification(
        self,
        target_user: schemas.TargetUser,
        access_control_priviliege_response: List[
            schemas.FamAccessControlPrivilegeCreateResponse
        ],
    ):
        try:
            granted_roles = ", ".join(
                item.detail.role.role_name
                for item in filter(
                    lambda res: res.status_code == HTTPStatus.OK,
                    access_control_priviliege_response,
                )
            )

            gc_notify_email_service = GCNotifyEmailService()
            email_response = gc_notify_email_service.send_delegated_admin_granted_email(
                schemas.GCNotifyGrantDelegatedAdminEmailParam(
                    **{
                        "send_to_email_address": target_user.email,
                        "application_name": access_control_priviliege_response[
                            0
                        ].detail.role.application.application_description,
                        "first_name": target_user.first_name,
                        "last_name": target_user.last_name,
                        "role_list_string": granted_roles,
                    }
                )
            )
            LOGGER.debug(f"Email is sent to {target_user.email}: {email_response}")
            return email_response
        except Exception as e:
            LOGGER.debug(
                f"Failure sending email to the new delegated admin {target_user.email}."
            )
            LOGGER.debug(f"Failure reason : {e}.")
