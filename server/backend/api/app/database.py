
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import config

LOGGER = logging.getLogger(__name__)

# Log SQL queries from SQLalcheny
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

SQLALCHEMY_DATABASE_URL = config.get_db_string()

Base = declarative_base()

_session_local = None


def get_db():
    try:
        # Initialize session local on first call
        global _session_local
        if not _session_local:
            LOGGER.debug("starting a new db session")
            engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
            LOGGER.debug("database engine created!")
            _session_local = sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine)

        db = _session_local()
        yield db

    except Exception:
        db.rollback()

    finally:
        db.commit()
        LOGGER.debug("closing db session")
        db.close()
