import logging

from .database import SessionLocal

LOGGER = logging.getLogger(__name__)


def get_db():
    try:
        LOGGER.debug("starting a new db session")
        db = SessionLocal()
        yield db
    finally:
        LOGGER.debug("closing db session")
        db.close()
