import logging
from typing import List

import sqlalchemy
from api.app.models import model as models
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

# from typing import

LOGGER = logging.getLogger(__name__)

def to_upper(elements: List[str]) -> List[str]:
    return [x.upper() for x in elements] if elements else None


def replace_str_list(elements: List[str], str_to_replace: str, replace_with: str) -> List[str]:
    return list(map(lambda r: r.replace(str_to_replace, replace_with), elements)) if elements else None


def get_primary_key(model: models) -> str:
    """recieves a declarative base model and returns the primary key that
    is defined for the base

    :param model: input declarative base model object
    :type model: sqlalchemy.ext.declarative
    :return: name of the primarly key column as a string
    :rtype: str
    """
    pk_name = inspect(model).primary_key[0].name
    LOGGER.debug(f"primary key for table {model.__table__}: {pk_name}")
    return pk_name


def get_highest_value(
    model: sqlalchemy.orm.decl_api.DeclarativeMeta, column_name: str, db: Session
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
    column_obj = getattr(model, column_name)
    query_result = db.query(func.max(column_obj)).first()
    LOGGER.debug(f"queryResult: {query_result}")
    return query_result


def get_next(model: sqlalchemy.orm.decl_api.DeclarativeMeta, db: Session) -> int:
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
    pk_name = get_primary_key(model)
    query_result = get_highest_value(model=model, column_name=pk_name, db=db)
    if query_result[0] is None:
        return 1
    else:
        return query_result[0] + 1


def get_application_id_from_name(db, application_name):
    # TODO: define types
    # TODO: define docstring
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_name == application_name)
        .one_or_none()
    )
    return application.application_id if application else None


def raise_http_exception(status_code: str, error_msg: str):
    LOGGER.info(error_msg)
    raise HTTPException(status_code=status_code, detail=error_msg)
