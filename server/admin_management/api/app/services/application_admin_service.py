import logging
from http import HTTPStatus
from sqlalchemy.orm import Session

from api.app import constants as famConstants
from api.app import schemas
from api.app.services.application_service import ApplicationService
from api.app.services.user_service import UserService
from api.app.repositories.application_admin_repository import ApplicationAdminRepository

from api.app.services import service_utils

LOGGER = logging.getLogger(__name__)


class ApplicationAdminService:
    def __init__(self, db: Session):
        self.application_admin_repo = ApplicationAdminRepository(db)
        self.application_service = ApplicationService(db)
        self.user_service = UserService(db)

    def create_application_admin(
        self, request: schemas.FamAppAdminCreate, requester: str
    ) -> schemas.FamAppAdminGet:
        # Request has information: user_name, user_type_code, application_id
        LOGGER.debug(
            f"Request for assigning an application admin to a user: {request}."
        )

        # Verify if user_type_code in enum (IDIR, BCEID)
        if (
            request.user_type_code != famConstants.UserType.IDIR
            and request.user_type_code != famConstants.UserType.BCEID
        ):
            error_msg = f"Invalid user type: {request.user_type_code}."
            service_utils.raise_http_exception(HTTPStatus.BAD_REQUEST, error_msg)

        # Verify if user already exists or add a new user
        fam_user = self.user_service.find_or_create(
            request.user_type_code, request.user_name, requester
        )

        # Verify if application exists
        fam_application = self.application_service.get_application(
            request.application_id
        )
        if not fam_application:
            error_msg = f"Application id {request.application_id} does not exist."
            service_utils.raise_http_exception(HTTPStatus.BAD_REQUEST, error_msg)

        # Verify if user is admin already
        fam_application_admin_user = self.application_admin_repo.get_application_admin(
            request.application_id, fam_user.user_id
        )
        if fam_application_admin_user:
            LOGGER.debug(
                "FamApplicationAdmin already exists with id: "
                + f"{fam_application_admin_user.application_admin_id}."
            )
            error_msg = "User is admin already."
            service_utils.raise_http_exception(HTTPStatus.CONFLICT, error_msg)
        else:
            # Create application admin if user is not admin yet
            fam_application_admin_user = (
                self.application_admin_repo.create_application_admin(
                    request.application_id, fam_user.user_id, requester
                )
            )

        fam_application_admin_user_dict = fam_application_admin_user.__dict__
        app_admin_user_assignment = schemas.FamAppAdminGet(
            **fam_application_admin_user_dict
        )
        LOGGER.debug(
            f"Application admin user assignment executed successfully: {app_admin_user_assignment}"
        )
        return app_admin_user_assignment

    def get_application_admin_by_id(self, application_admin_id: int):
        return self.application_admin_repo.get_application_admin_by_id(
            application_admin_id
        )
