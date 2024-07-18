import os
import logging

from api.app.constants import AppEnv, ApiInstanceEnv, AwsTargetEnv


LOGGER = logging.getLogger(__name__)


def get_aws_target_env() -> AwsTargetEnv:
    # target_env is assigned from gov's AWS platform, does not exist in local (None).
    return os.environ.get("target_env")


def is_on_aws_prod() -> bool:
    return get_aws_target_env() == AwsTargetEnv.PROD


def use_api_instance_by_app_env(app_env: str | None) -> ApiInstanceEnv:
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
