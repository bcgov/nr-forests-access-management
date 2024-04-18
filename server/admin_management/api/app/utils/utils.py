import logging
from fastapi import HTTPException

LOGGER = logging.getLogger(__name__)


def raise_http_exception(status_code: str, error_msg: str):
    LOGGER.info(error_msg)
    raise HTTPException(status_code=status_code, detail=error_msg)


def remove_app_env_suffix(name: str):
    suffix_list = ["_DEV", "_TEST", "_PROD"]
    for suffix in suffix_list:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name
