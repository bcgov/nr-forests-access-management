import os
import logging

from api.app.constants import AppEnv, ApiInstanceEnv, AwsTargetEnv
from api.config.config import is_on_aws_prod


LOGGER = logging.getLogger(__name__)


def use_api_instance_by_app_env(app_env: str) -> ApiInstanceEnv:
    """
    FAM PROD environment supports (DEV/TET/PROD) integrated applications.
    Only PROD application at FAM PROD uses API instance in PROD.
    Lower FAM environment uses only TEST instance.
    Ref @FAM Wiki: https://github.com/bcgov/nr-forests-access-management/wiki/Environment-Management
    """
    api_instance_env = ApiInstanceEnv.TEST  # API TEST instance as default.
    if is_on_aws_prod() and (
        # either PROD app or no app_env (which is FAM, FAM has no app_env)
        app_env == AppEnv.APP_ENV_TYPE_PROD
        or not app_env
    ):
        api_instance_env = ApiInstanceEnv.PROD

    LOGGER.info(f"Use api instance environment -- {api_instance_env}")
    return api_instance_env
