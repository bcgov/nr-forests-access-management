
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import config

LOGGER = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = config.get_db_string()

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
LOGGER.debug("database engine created!")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
