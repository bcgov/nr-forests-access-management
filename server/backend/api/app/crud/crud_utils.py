import logging
import os
from typing import List, Optional

import sqlalchemy
from sqlalchemy.orm import DeclarativeMeta
from api.app.constants import (
    APPLICATION_FAM,
    ERROR_CODE_INVALID_APPLICATION_ID,
    ApiInstanceEnv,
    AppEnv,
    AwsTargetEnv,
)
from api.app.crud import crud_application
from api.app.models import FamApplicationModel
from api.app.utils.utils import raise_http_exception
from sqlalchemy import func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


def to_upper(elements: List[str]) -> List[str]:
    return [x.upper() for x in elements] if elements else None


def replace_str_list(
    elements: List[str], str_to_replace: str, replace_with: str
) -> List[str]:
    return (
        list(map(lambda r: r.replace(str_to_replace, replace_with), elements))
        if elements
        else None
    )


def get_primary_key_name(instance: DeclarativeMeta) -> str:
    """
    Given a SQLAlchemy model instance, return the name of the primary key.

    Args:
        instance (DeclarativeMeta): An instance of a SQLAlchemy model.

    Returns:
        str: The name of the primary key for the given model instance.
    """
    # Inspect the instance to get its primary key
    primary_key = inspect(instance).mapper.primary_key[0]
    # Return the name of the primary key attribute
    return primary_key.name


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


def get_next(model: DeclarativeMeta, db: Session) -> int:
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


def is_app_admin(
    application_id: int,
    db: Session,
    access_roles: Optional[List[str]] = None,
):
    application = crud_application.get_application(application_id=application_id, db=db)
    if not application:
        error_msg = f"Application ID {application_id} not found"
        raise_http_exception(
            error_msg=error_msg, error_code=ERROR_CODE_INVALID_APPLICATION_ID
        )

    admin_role = f"{application.application_name.upper()}_ADMIN"

    if access_roles and admin_role in access_roles:
        return True
    return False


def get_aws_target_env() -> AwsTargetEnv:
    # TARGET_ENV is assigned from gov's AWS platform, does not exist in local (None).
    return os.environ.get("TARGET_ENV")


def is_on_aws_prod() -> bool:
    return get_aws_target_env() == AwsTargetEnv.PROD


def use_api_instance_by_app(application: FamApplicationModel) -> ApiInstanceEnv:
    """
    FAM PROD environment supports (DEV/TET/PROD) integrated applications.
    Only PROD application at FAM PROD uses API instance in PROD.
    Lower FAM environment uses only TEST instance.
    Ref @FAM Wiki: https://github.com/bcgov/nr-forests-access-management/wiki/Environment-Management
    """
    api_instance_env = ApiInstanceEnv.TEST  # API TEST instance as default.
    if is_on_aws_prod() and (
        # either PROD app or app is FAM
        application.app_environment == AppEnv.APP_ENV_TYPE_PROD
        or application.application_name == APPLICATION_FAM
    ):
        api_instance_env = ApiInstanceEnv.PROD

    LOGGER.info(f"Use api instance environment -- {api_instance_env}")
    return api_instance_env
