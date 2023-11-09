import logging
import os

LOGGER = logging.getLogger(__name__)


class MissingEnvironmentVariable(Exception):
    def __init__(self, env_var_name):
        self.message = (
            f"The required environment variable {env_var_name} has not "
            + "been populated"
        )
        super().__init__(self.message)


def get_env_var(env_var_name):
    if env_var_name not in os.environ:
        raise MissingEnvironmentVariable(env_var_name)
    return os.environ.get(env_var_name)


def get_root_path():
    root_path = ""

    api_gateway_stage_name = os.environ.get("API_GATEWAY_STAGE_NAME")
    if api_gateway_stage_name:
        root_path = f"/{api_gateway_stage_name}"

    return root_path


def is_on_aws():
    return os.environ.get("DB_SECRET") is not None  # This key only presents on aws.


def get_allow_origins():
    allow_origins = [get_env_var("ALLOW_ORIGIN")] if is_on_aws() else ["*"]
    LOGGER.info(f"allow_origins -- {allow_origins}")
    return allow_origins
