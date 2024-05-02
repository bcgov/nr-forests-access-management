import logging
from sqlalchemy.orm import Session

from api.app.models import model as models
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

    def update_user_business_guid(self, user_id: int, business_guid: str):
        """
        The method only updates business_guid for user if necessary.
        The calling method should make sure "business_guid" is correct for the
        user (e.g.,searched from IDIM). This method does not do BCeID user 
        search.
        :param user_id: The user to be updated on.
        :param business_id: The business_guid value to updated for the user.
        """
        LOGGER.debug(f"update_user_business_guid() with: user_id: {user_id} " +
                     f"business_guid: {business_guid}")
        if business_guid is not None:
            user = self.user_repo.get_user(user_id)
            if (
                user.business_guid is None 
                or business_guid != user.business_guid
            ):
                # update user when necessary.
                self.user_repo.update(user_id, {
                    models.FamUser.business_guid: business_guid
                })
        return self.user_repo.get_user(user_id)
