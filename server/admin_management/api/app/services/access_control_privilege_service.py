import logging
from http import HTTPStatus
from sqlalchemy.orm import Session
from typing import List

from api.app import constants as famConstants
from api.app import schemas

from api.app.services.user_service import UserService
from api.app.services.role_service import RoleService
from api.app.repositories.access_control_privilege_repository import (
    AccessControlPrivilegeRepository,
)

from api.app.utils import utils

LOGGER = logging.getLogger(__name__)


class AccessControlPrivilegeService:
    def __init__(self, db: Session):
        self.user_service = UserService(db)
        self.role_service = RoleService(db)
        self.access_control_privilege_repository = AccessControlPrivilegeRepository(db)

    def get_use_role_by_user_id_and_role_id(self, user_id: int, role_id: int):
        return self.access_control_privilege_repository.get_use_role_by_user_id_and_role_id(
            user_id, role_id
        )

    def create_access_control_privilege(
        self, request: schemas.FamAccessControlPrivilegeCreate, requester: str
    ) -> schemas.FamAccessControlPrivilegeGet:
        LOGGER.debug(
            f"Request for assigning access role privilege to a user: {request}."
        )

        # Verify if user already exists or add a new user
        fam_user = self.user_service.find_or_create(
            request.user_type_code, request.user_name, requester
        )

        # Verify if role exists.
        fam_role = self.role_service.get_role(request.role_id)
        if not fam_role:
            error_msg = f"Role id {request.role_id} does not exist."
            utils.raise_http_exception(HTTPStatus.BAD_REQUEST, error_msg)

        # For now, delegated admin access control privilege focus on abstract role
        # Role is a 'Abstract' type, create role assignment with forst client child role.
        require_child_role = (
            fam_role.role_type_code == famConstants.RoleType.ROLE_TYPE_ABSTRACT
        )

        access_control_privilege_return: List[schemas.FamAccessControlPrivilegeGet] = []

        if require_child_role:
            LOGGER.debug(
                f"Role {fam_role.role_name} requires child role "
                "for creating delegate admin access control privilege."
            )

            if (
                not hasattr(request, "forest_client_number")
                or request.forest_client_number is None
            ):
                error_msg = (
                    "Invalid role assignment request. Cannot assign user "
                    + f"{request.user_name} to abstract role {fam_role.role_name}"
                )
                utils.raise_http_exception(HTTPStatus.BAD_REQUEST, error_msg)

            for forest_number in request.forest_client_number:
                child_role = self.role_service.find_or_create_forest_client_child_role(
                    forest_number, fam_role, requester
                )
                associate_role_id = child_role.role_id

                # Check if user privilege already exists
                fam_access_control_privilege = self.get_use_role_by_user_id_and_role_id(
                    fam_user.user_id, associate_role_id
                )

                if fam_access_control_privilege:
                    LOGGER.debug(
                        "FamAccessControlPrivilege already exists with id: "
                        + f"{fam_access_control_privilege.access_control_privilege_id}."
                    )

                    error_msg = (
                        "User already has the access control privilege for role"
                        + f"{fam_role.role_name}"
                        + ", role id"
                        + f"{fam_role.role_id}"
                    )
                    utils.raise_http_exception(HTTPStatus.CONFLICT, error_msg)
                else:
                    fam_access_control_privilege = self.access_control_privilege_repository.create_access_control_privilege(
                        fam_user.user_id, associate_role_id, requester
                    )
                    fam_access_control_privilege_dict = (
                        fam_access_control_privilege.__dict__
                    )
                    access_control_privilege_return.append(
                        schemas.FamAccessControlPrivilegeGet(
                            **fam_access_control_privilege_dict
                        )
                    )
        else:
            fam_access_control_privilege = self.access_control_privilege_repository.create_access_control_privilege(
                fam_user.user_id, fam_role.role_id, requester
            )
            fam_access_control_privilege_dict = fam_access_control_privilege.__dict__
            access_control_privilege_return.append(
                schemas.FamAccessControlPrivilegeGet(
                    **fam_access_control_privilege_dict
                )
            )

        LOGGER.debug(
            f"Creating access control privilege executed successfully: {access_control_privilege_return}"
        )

        return access_control_privilege_return
