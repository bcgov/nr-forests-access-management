import logging

from .database import SessionLocal

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
