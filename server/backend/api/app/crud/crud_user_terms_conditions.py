import logging
from sqlalchemy.orm import Session
from http import HTTPStatus

from api.app.models.model import FamUserTermsConditions
from api.app.schemas import Requester
from api.app.utils.utils import raise_http_exception
from api.app.crud.crud_utils import is_requester_external_delegated_admin


LOGGER = logging.getLogger(__name__)


def get_user_terms_conditions_by_user_id_and_version(
    db: Session, user_id: int, version: str
):
    return (
        db.query(FamUserTermsConditions)
        .filter(
            FamUserTermsConditions.user_id == user_id,
            FamUserTermsConditions.version == version,
        )
        .one_or_none()
    )


def require_accept_terms_and_conditions(
    db: Session, requester: Requester, version: str
) -> bool:
    """
    Return False if found record (means user already accepted terms and conditions)
    Return True if not found (means user needs to accept terms and conditions)
    """
    if is_requester_external_delegated_admin(
        db, requester
    ) and not get_user_terms_conditions_by_user_id_and_version(
        db, requester.user_id, version
    ):
        return True
    return False


def create_user_terms_conditions(
    db: Session, user_id: int, version: str, requester: str
) -> FamUserTermsConditions:
    LOGGER.debug(
        f"Creating user terms conditions acceptance record for user {user_id} and version {version}"
    )

    if get_user_terms_conditions_by_user_id_and_version(db, user_id, version):
        error_msg = "User already accepted terms and conditions."
        raise_http_exception(error_msg=error_msg, status_code=HTTPStatus.CONFLICT)

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
