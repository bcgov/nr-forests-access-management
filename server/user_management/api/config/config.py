import logging
import os

LOGGER = logging.getLogger(__name__)


def get_root_path():
    root_path = ""

    api_gateway_stage_name = os.environ.get("API_GATEWAY_STAGE_NAME")
    if api_gateway_stage_name:
        root_path = f"/{api_gateway_stage_name}"

    return root_path
