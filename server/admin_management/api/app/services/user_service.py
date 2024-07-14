import logging

from api.app.models import model as models
from api.app.repositories.user_repository import UserRepository
from api.app.schemas import FamUserDto, TargetUser
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def get_user_by_domain_and_name(self, user_type_code: str, user_name: str):
        return self.user_repo.get_user_by_domain_and_name(user_type_code, user_name)

    def get_user_by_cognito_user_id(self, cognito_user_id: str):
        return self.user_repo.get_user_by_cognito_user_id(cognito_user_id)

    def get_user_by_domain_and_guid(self, user_type_code: str, user_guid: str):
        return self.user_repo.get_user_by_domain_and_guid(user_type_code, user_guid)

    def get_users(self):
        return self.user_repo.get_users()

    def find_or_create(
        self, user_type_code: str, user_name: str, user_guid: str, requester: str
    ):
        LOGGER.debug(
            f"Request for finding or creating a user with user_type: {user_type_code}, "
            + f"user_name: {user_name}."
        )

        fam_user = self.get_user_by_domain_and_guid(user_type_code, user_guid)
        if not fam_user:
            fam_user_by_domain_and_name = self.get_user_by_domain_and_name(
                user_type_code, user_name
            )
            # if not found user by user_guid, but found user by domain and name
            # in the case of historical FAM user that has no user_guid stored
            # add their user_guid
            if (
                fam_user_by_domain_and_name
                and not fam_user_by_domain_and_name.user_guid
            ):
                self.user_repo.update(
                    fam_user_by_domain_and_name.user_id,
                    {models.FamUser.user_guid: user_guid},
                    requester,
                )
                LOGGER.debug(
                    f"User {fam_user_by_domain_and_name.user_id} found, updated to store their user_guid."
                )
                return fam_user_by_domain_and_name
            # if not found user by user_guid, and not found user by domain and username,
            # or found user by domain and username, but user guid does not match (this is the edge case that could happen when username changed from IDP provider)
            # create a new user
            else:
                request_user = FamUserDto(
                    **{
                        "user_type_code": user_type_code,
                        "user_name": user_name,
                        "user_guid": user_guid,
                        "create_user": requester,
                    }
                )

                fam_user_new = self.user_repo.create_user(request_user)
                LOGGER.debug(f"User created: {fam_user_new.user_id}.")
                return fam_user_new

        LOGGER.debug(f"User {fam_user.user_id} found.")
        # update user_name if needs
        fam_user = self.update_user_name(fam_user, user_name, requester)
        return fam_user

    def update_user_name(
        self,
        user: models.FamUser,
        user_name_for_update: str,
        requester: str,  # cognito_user_id
    ):
        if user.user_name.lower() != user_name_for_update.lower():
            self.user_repo.update(
                user.user_id,
                {models.FamUser.user_name: user_name_for_update},
                requester,
            )
            LOGGER.debug(
                f"Updated the username of user {user.user_id} to {user_name_for_update}."
            )
            return self.user_repo.get_user(user.user_id)
        return user

    def update_user_business_guid(
        self, user_id: int, business_guid: str, requester: str  # cognito_user_id
    ):
        """
        The method only updates business_guid for user if necessary.
        The calling method should make sure "business_guid" is correct for the
        user (e.g.,searched from IDIM). This method does not do BCeID user
        search.
        :param user_id: The user to be updated on.
        :param business_id: The business_guid value to updated for the user.
        :param requester: This is requester's cognito_user_id when updating
            record from the 'update_user'.
        """
        LOGGER.debug(
            f"update_user_business_guid() with: user_id: {user_id} "
            + f"business_guid: {business_guid} from requester: {requester}"
        )
        if business_guid is not None:
            user = self.user_repo.get_user(user_id)
            if user.business_guid is None or business_guid != user.business_guid:
                # update user when necessary.
                self.user_repo.update(
                    user_id, {models.FamUser.business_guid: business_guid}, requester
                )
        return self.user_repo.get_user(user_id)

    def update_common_user_properties(
        self, user_id: int, target_user: TargetUser, requester: str  # cognito_user_id
    ):
        """
        :param user_id: The user to be updated on.
        :param target_user: Type of TargetUser. Contains the properties' values for update.
        :param requester: This is requester's cognito_user_id when updating
            record from the 'update_user'.
        """
        self.user_repo.update(
            user_id,
            # first_name, last_name, email
            {
                models.FamUser.first_name: target_user.first_name,
                models.FamUser.last_name: target_user.last_name,
                models.FamUser.email: target_user.email
            },
            requester,
        )
        LOGGER.debug(
            f"Common user properties were updated to fam_user {user_id}."
        )
        return self.user_repo.get_user(user_id)
