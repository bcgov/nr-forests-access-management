import logging
from sqlalchemy.orm import Session

from api.app.models.model import FamUserTermsConditions


LOGGER = logging.getLogger(__name__)


def if_needs_accept_terms_and_conditions(
    db: Session, user_id: int, version_id: int
) -> bool:
    return (
        True
        if db.query(FamUserTermsConditions)
        .filter(
            FamUserTermsConditions.user_id == user_id,
            FamUserTermsConditions.version_id == version_id,
        )
        .one_or_none()
        else False
    )


def create_user_terms_conditions(
    db: Session, user_id: int, version_id: int, requester: str
) -> FamUserTermsConditions:
    LOGGER.debug(
        f"Creating user terms conditions acceptance record for user {user_id} and version {version_id}"
    )

    new_user_terms_conditions = FamUserTermsConditions(
        **{
            "user_id": user_id,
            "version_id": version_id,
            "create_user": requester,
        }
    )
    db.add(new_user_terms_conditions)
    db.flush()
    db.refresh(new_user_terms_conditions)
    return new_user_terms_conditions
