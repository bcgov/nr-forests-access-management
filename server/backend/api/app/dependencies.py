import logging
from .database import SessionLocal
from .jwt_validation import get_rsa_key

LOGGER = logging.getLogger(__name__)


def get_db():
    try:
        LOGGER.debug("starting a new db session")
        db = SessionLocal()
        yield db

    except Exception:
        db.rollback()

    finally:
        db.commit()
        LOGGER.debug("closing db session")
        db.close()
