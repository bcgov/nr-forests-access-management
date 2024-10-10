import logging
from http import HTTPStatus

from api.app.repositories.application_admin_repository import \
    ApplicationAdminRepository
from api.app.schemas import schemas
from api.app.services.application_service import ApplicationService
from api.app.services.user_service import UserService
from api.app.utils import utils
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class ApplicationAdminService:
    def __init__(self, db: Session):
        self.application_admin_repo = ApplicationAdminRepository(db)
        self.application_service = ApplicationService(db)
        self.user_service = UserService(db)

    def get_application_admins(self) -> schemas.FamAppAdminGetResponse:
        return self.application_admin_repo.get_application_admins()

    def get_application_admin_by_id(
        self, application_admin_id: int
    ) -> schemas.FamAppAdminGetResponse:
        return self.application_admin_repo.get_application_admin_by_id(
            application_admin_id
        )

    def create_application_admin(
        self, request: schemas.FamAppAdminCreateRequest,
        target_user: schemas.TargetUser, requester: str
    ) -> schemas.FamAppAdminGetResponse:
        # Request has information: user_name, user_type_code, application_id
        LOGGER.debug(
            f"Request for assigning an application admin to a user: {request}."
        )

        # Verify if user already exists or add a new user
        fam_user = self.user_service.find_or_create(
            request.user_type_code, request.user_name, request.user_guid, requester
        )
        fam_user = self.user_service.update_user_properties_from_verified_target_user(
            fam_user.user_id, target_user, requester
        )

        # Verify if user is admin already
        fam_application_admin_user = (
            self.application_admin_repo.get_application_admin_by_app_and_user_id(
                request.application_id, fam_user.user_id
            )
        )
        if fam_application_admin_user:
            LOGGER.debug(
                "FamApplicationAdmin already exists with id: "
                + f"{fam_application_admin_user.application_admin_id}."
            )
            error_msg = "User is admin already."
            utils.raise_http_exception(
                status_code=HTTPStatus.CONFLICT,
                error_msg=error_msg)
        else:
            # Create application admin if user is not admin yet
            fam_application_admin_user = (
                self.application_admin_repo.create_application_admin(
                    request.application_id, fam_user.user_id, requester
                )
            )

        fam_application_admin_user_dict = fam_application_admin_user.__dict__
        app_admin_user_assignment = schemas.FamAppAdminGetResponse(
            **fam_application_admin_user_dict
        )
        LOGGER.debug(
            f"Application admin user assignment executed successfully: {app_admin_user_assignment}"
        )
        return app_admin_user_assignment

    def delete_application_admin(self, application_admin_id: int):
        return self.application_admin_repo.delete_application_admin(
            application_admin_id
        )
