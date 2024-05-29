import logging
from sqlalchemy.orm import Session
from typing import List, Optional

from api.app.models import model as models
from api.app import schemas


LOGGER = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Get ---

    def get_user(self, user_id) -> Optional[models.FamUser]:
        return self.db.query(models.FamUser).get(user_id)

    def get_users(self) -> List[models.FamUser]:
        return self.db.query(models.FamUser).all()

    def get_user_by_domain_and_name(
        self, user_type_code: str, user_name: str
    ) -> models.FamUser:
        fam_user: models.FamUser = (
            self.db.query(models.FamUser)
            .filter(
                models.FamUser.user_type_code == user_type_code,
                models.FamUser.user_name.ilike(user_name),
            )
            .one_or_none()
        )
        LOGGER.debug(
            f"fam_user {str(fam_user.user_id) + ' found' if fam_user else 'not found'}."
        )
        return fam_user

    def get_user_by_cognito_user_id(self, cognito_user_id: str) -> models.FamUser:
        return (
            self.db.query(models.FamUser)
            .filter(models.FamUser.cognito_user_id == cognito_user_id)
            .one_or_none()
        )

    def get_user_by_domain_and_guid(
        self, user_type_code: str, user_guid: str
    ) -> models.FamUser:
        return (
            self.db.query(models.FamUser)
            .filter(
                models.FamUser.user_type_code == user_type_code,
                models.FamUser.user_guid == user_guid,
            )
            .one_or_none()
        )

    # --- Create ---

    def create_user(self, fam_user: schemas.FamUserDto) -> models.FamUser:
        user_dict = fam_user.model_dump()
        db_item = models.FamUser(**user_dict)
        self.db.add(db_item)
        self.db.flush()
        return db_item

    # --- Update ---

    def update(self, user_id, update_values: dict, requester: str) -> int:
        LOGGER.debug(
            f"Update on FamUser {user_id} with values: {update_values} "
            + f"for requester {requester}"
        )
        update_count = (
            self.db.query(models.FamUser)
            .filter(models.FamUser.user_id == user_id)
            .update({**update_values, models.FamUser.update_user: requester})
        )
        LOGGER.debug(f"{update_count} row updated.")
        return update_count
