import logging
from sqlalchemy.orm import Session

from api.app.models import model as models
from api.app import schemas


LOGGER = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

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

    def create_user(self, fam_user: schemas.FamUser) -> models.FamUser:
        LOGGER.debug(f"Creating fam user: {fam_user}")

        fam_user_dict = fam_user.model_dump()
        db_item = models.FamUser(**fam_user_dict)
        self.db.add(db_item)
        self.db.flush()
        return db_item
