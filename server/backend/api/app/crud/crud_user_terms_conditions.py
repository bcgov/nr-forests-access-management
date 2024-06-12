import logging
from sqlalchemy.orm import Session
from http import HTTPStatus

from api.app.models.model import FamUserTermsConditions
from api.app.utils.utils import raise_http_exception


LOGGER = logging.getLogger(__name__)


def require_accept_terms_and_conditions(
    db: Session, user_id: int, version: str
) -> bool:
    """
    Return False if found record (means user already accepted terms and conditions)
    Return True if not found (means user needs to accept terms and conditions)
    """
    return (
        False
        if db.query(FamUserTermsConditions)
        .filter(
            FamUserTermsConditions.user_id == user_id,
            FamUserTermsConditions.version == version,
        )
        .one_or_none()
        else True
    )


def create_user_terms_conditions(
    db: Session, user_id: int, version: str, requester: str
) -> FamUserTermsConditions:
    LOGGER.debug(
        f"Creating user terms conditions acceptance record for user {user_id} and version {version}"
    )

    if not require_accept_terms_and_conditions(db, user_id, version):
        error_msg = "User already accepted terms and conditions."
        raise_http_exception(status_code=HTTPStatus.CONFLICT, error_msg=error_msg)

    new_user_terms_conditions = FamUserTermsConditions(
        **{
            "user_id": user_id,
            "version": version,
            "create_user": requester,
        }
    )
    db.add(new_user_terms_conditions)
    db.flush()
    db.refresh(new_user_terms_conditions)
    return new_user_terms_conditions
