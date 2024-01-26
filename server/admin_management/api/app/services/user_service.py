import logging
from sqlalchemy.orm import Session

from api.app.schemas import FamUserDto
from api.app.repositories.user_repository import UserRepository


LOGGER = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def get_user_by_domain_and_name(self, user_type_code: str, user_name: str):
        return self.user_repo.get_user_by_domain_and_name(user_type_code, user_name)

    def get_user_by_cognito_user_id(self, cognito_user_id: str):
        return self.user_repo.get_user_by_cognito_user_id(cognito_user_id)

    def get_users(self):
        return self.user_repo.get_users()

    def find_or_create(self, user_type_code: str, user_name: str, requester: str):
        LOGGER.debug(
            f"Request for finding or creating a user with user_type: {user_type_code}, "
            + f"user_name: {user_name}."
        )

        fam_user = self.get_user_by_domain_and_name(user_type_code, user_name)
        if not fam_user:
            request_user = FamUserDto(
                **{
                    "user_type_code": user_type_code,
                    "user_name": user_name,
                    "create_user": requester,
                }
            )

            fam_user = self.user_repo.create_user(request_user)
            LOGGER.debug(f"User created: {fam_user.user_id}.")
            return fam_user

        LOGGER.debug(f"User {fam_user.user_id} found.")
        return fam_user
