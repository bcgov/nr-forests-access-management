
import logging

from . import config

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

LOGGER = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = config.getDBString()

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
LOGGER.debug("database engine created!")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
