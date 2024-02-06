import logging
from http import HTTPStatus
from typing import List

from api.app import constants as famConstants
from api.app import schemas

from api.app.integration.forest_client_integration import ForestClientService
from api.app.repositories.access_control_privilege_repository import \
    AccessControlPrivilegeRepository
from api.app.services.role_service import RoleService
from api.app.services.user_service import UserService
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

    def create_access_control_privilege_many(
        self, request: schemas.FamAccessControlPrivilegeCreateRequest, requester: str
    ) -> List[schemas.FamAccessControlPrivilegeCreateResponse]:
        LOGGER.debug(
            f"Request for assigning access role privilege to a user: {request}."
        )

        # Verify if user already exists or add a new user
        fam_user = self.user_service.find_or_create(
            request.user_type_code, request.user_name, requester
        )

        # Verify if role exists
        fam_role = self.role_service.get_role_by_id(request.role_id)
        if not fam_role:
            error_msg = f"Role id {request.role_id} does not exist."
            utils.raise_http_exception(HTTPStatus.BAD_REQUEST, error_msg)

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
                utils.raise_http_exception(HTTPStatus.BAD_REQUEST, error_msg)

            for forest_client_number in request.forest_client_numbers:
                # validate the forest client number
                validator = ForestClientValidator(forest_client_number)
                error_msg = ""
                if not validator.forest_client_number_exists():
                    error_msg = (
                        "Invalid access control privilege request. "
                        + f"Forest client number {forest_client_number} does not exist."
                    )
                elif not validator.forest_client_active():
                    error_msg = (
                        "Invalid access control privilege request. "
                        + f"Forest client number {forest_client_number} is not in active status: "
                        + f"{validator.get_forest_client()[famConstants.FOREST_CLIENT_STATUS['KEY']]}"
                    )

                if error_msg != "":
                    # raise error when adding privilege for only one forest client number
                    if len(request.forest_client_numbers) == 1:
                        utils.raise_http_exception(HTTPStatus.BAD_REQUEST, error_msg)
                    else:
                        create_return_list.append(
                            schemas.FamAccessControlPrivilegeCreateResponse(
                                **{
                                    "status_code": HTTPStatus.BAD_REQUEST,
                                    "detail": schemas.FamAccessControlPrivilegeCreateErrorDto(
                                        **{
                                            "user_id": fam_user.user_id,
                                            "user": fam_user,
                                            "forest_client_number": forest_client_number,
                                            "parent_role": fam_role,
                                        }
                                    ),
                                    "error_message": error_msg,
                                }
                            )
                        )
                else:
                    # Check if child role exists or add a new child role
                    child_role = (
                        self.role_service.find_or_create_forest_client_child_role(
                            forest_client_number, fam_role, requester
                        )
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


class ForestClientValidator:
    """
    Purpose: More validations on inputs (other than basic validations) and
             business rules validations (if any).
    Cautious: Do not instantiate the class for more than one time per request.
              It calls Forest Client API remotely if needs to.
    """

    LOGGER = logging.getLogger(__name__)

    def __init__(self, forest_client_number: str):
        LOGGER.debug(
            f"Validator '{self.__class__.__name__}' with input '{forest_client_number}'."
        )

        # Note - this value should already be validated from schema input validation.
        if forest_client_number is not None:
            fc_api = ForestClientService()

            # Locally stored (if any) for later use to prevent api calls again.
            # Exact client number search - should only contain 1 result.
            self.fc = fc_api.find_by_client_number(forest_client_number)
            LOGGER.debug(f"Forest Client(s) retrieved: {self.fc}")

    def forest_client_number_exists(self) -> bool:
        # Exact client number search - should only contain 1 result.
        return len(self.fc) == 1

    def forest_client_active(self) -> bool:
        return (
            (
                self.get_forest_client()[famConstants.FOREST_CLIENT_STATUS["KEY"]]
                == famConstants.FOREST_CLIENT_STATUS["CODE_ACTIVE"]
            )
            if self.forest_client_number_exists()
            else False
        )

    def get_forest_client(self):
        return self.fc[0] if self.forest_client_number_exists() else None
