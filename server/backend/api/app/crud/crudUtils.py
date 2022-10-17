import logging

import sqlalchemy
from api.app.models import model as models
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


def getPrimaryKey(model: models) -> str:
    """recieves a declarative base model and returns the primary key that
    is defined for the base

    :param model: input declarative base model object
    :type model: sqlalchemy.ext.declarative
    :return: name of the primarly key column as a string
    :rtype: str
    """
    pkName = inspect(model).primary_key[0].name
    LOGGER.debug(f"primary key for table {model.__table__}: {pkName}")
    return pkName


def getHighestValue(
    model: sqlalchemy.orm.decl_api.DeclarativeMeta, columnName: str, db: Session
):
    """Queries for the highest value found for a particular column

    :param model: input sqlalchemy model to be queried
    :type model: sqlalchemy.orm.decl_api.DeclarativeMeta
    :param columnName: name of the column who's value we want to retrieve the
        highest existing value
    :type columnName: str
    :param db: sql alchemy database session object
    :type db: Session
    :return: an integer with the current highest value found for the given
        column
    :rtype: int
    """
    columnObj = getattr(model, columnName)
    queryResult = db.query(func.max(columnObj)).first()
    LOGGER.debug(f"queryResult: {queryResult}")
    return queryResult


def getNext(model: sqlalchemy.orm.decl_api.DeclarativeMeta, db: Session) -> int:
    """calculates the next increment for the given model.  This is
    created because in development the autoincrement / populate feature
    for sqllite databases does not always work.

    :param model: input declarative base model
    :type model: sqlalchemy.orm.decl_api.DeclarativeMeta
    :param db: sql alchemy database session object
    :type db: sqlalchemy.orm.session.Session
    :return: the next value for the primary key
    :rtype: int
    """
    pkName = getPrimaryKey(model)
    queryResult = getHighestValue(model, pkName, db)
    if queryResult[0] is None:
        return 1
    else:
        return queryResult[0] + 1


def getUpdateUser():
    """A stub method, once the api has been integrated w/ Cognito the update
    user will come from the JWT token that is a result of the authentication.
    """
    return "default updateuser"


def getAddUser():
    """A stub method, once the api has been integrated w/ Cognito the update
    user will come from the JWT token that is a result of the authentication.
    """
    return "default adduser"


def raiseHTTPException(status_code: str, error_msg: str):
    LOGGER.error(error_msg)
    raise HTTPException(status_code=status_code, detail=error_msg)
