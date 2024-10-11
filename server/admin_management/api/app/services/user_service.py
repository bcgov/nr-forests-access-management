import logging

from api.app.constants import UserType
from api.app.models import model as models
from api.app.repositories.user_repository import UserRepository
from api.app.schemas.schemas import FamUserDto, TargetUser
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
        self, user_type_code: str, user_name: str, user_guid: str, requester_cognito_user_id: str
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
                    requester_cognito_user_id,
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
                        "create_user": requester_cognito_user_id,
                    }
                )

                fam_user_new = self.user_repo.create_user(request_user)
                LOGGER.debug(f"User created: {fam_user_new.user_id}.")
                return fam_user_new

        LOGGER.debug(f"User {fam_user.user_id} found.")
        # update user_name if needs
        fam_user = self.update_user_name(fam_user, user_name, requester_cognito_user_id)
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

    def update_user_properties_from_verified_target_user(
        self, user_id: int, target_user: TargetUser, requester_cognito_user_id: str
    ):
        """
        This is to update fam_user's properties from verified_target_user.
        'verified_target_user' user is searched from IDIM proxy service.
        Currently few properties are updated. 'user_name' is left out for different update.
        :param user_id: The user to be updated on.
        :param target_user: Type of TargetUser.
            Contains the user's latest property values for update.
        :param requester: This is requester's cognito_user_id when updating
            record from the 'update_user'.
        """
        user_type_code = target_user.user_type_code
        # update first_name, last_name, email
        first_name = target_user.first_name
        last_name = target_user.last_name
        email = target_user.email
        LOGGER.debug(
            f"Add first_name: {first_name}, last_name: {last_name}, "
            f"email: {email} for fam_user update."
        )
        properties_to_update = {
            models.FamUser.first_name: first_name,
            models.FamUser.last_name: last_name,
            models.FamUser.email: email
        }
        # update business_guid when necessary
        business_guid = target_user.business_guid
        if user_type_code == UserType.BCEID and business_guid:
            LOGGER.debug(f"Add business_guid: {business_guid} for fam_user update.")
            # add additional property to 'properties_to_update'
            properties_to_update = {
                **properties_to_update,
                models.FamUser.business_guid: business_guid
            }

        self.user_repo.update(
            user_id,
            properties_to_update,
            requester_cognito_user_id,
        )

        LOGGER.debug(
            f"fam_user {user_id} properties were updated."
        )
        return self.user_repo.get_user(user_id)
