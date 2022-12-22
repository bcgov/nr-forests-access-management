
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import config

LOGGER = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = config.get_db_string()

Base = declarative_base()


def get_db():
    try:
        # TODO: Was this stuff initialized (engion and sessionmaker) for
        # performance? Moved it in here to get tests to pass on GitHub
        LOGGER.debug("starting a new db session")
        engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
        LOGGER.debug("database engine created!")
        session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = session_local()
        yield db

    except Exception:
        db.rollback()

    finally:
        db.commit()
        LOGGER.debug("closing db session")
        db.close()
