
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from api.config import config

LOGGER = logging.getLogger(__name__)

# Log SQL queries from SQLalcheny
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

Base = declarative_base()

_db_url = None
_session_local = None


def get_db():
    try:
        # Initialize session local on first call
        global _db_url
        global _session_local
        if not _session_local:
            LOGGER.debug("starting a new db session")

            if not _db_url:
                _db_url = config.get_db_string()
            engine = create_engine(_db_url, echo=False)
            LOGGER.debug("database engine created!")
            _session_local = sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine)

        db = _session_local()
        yield db

    except Exception as e:
        LOGGER.debug(f"db session excpetion: {e}")
        db.rollback()

    finally:
        db.commit()
        LOGGER.debug("closing db session")
        db.close()
