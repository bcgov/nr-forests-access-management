import logging
from http import HTTPStatus

from api.app.constants import ERROR_CODE_INVALID_OPERATION
from fastapi import HTTPException
from requests import Response

LOGGER = logging.getLogger(__name__)


def raise_http_exception(
    error_msg: str,
    error_code: str = ERROR_CODE_INVALID_OPERATION,  # default, please override if necessary
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST,  # default http status, please override if necessary
):
    LOGGER.debug(error_msg)
    raise HTTPException(
        status_code=status_code,
        detail={
            "code": error_code,
            "description": error_msg,
        }
    )


def remove_app_env_suffix(name: str):
    suffix_list = ["_DEV", "_TEST", "_PROD"]
    for suffix in suffix_list:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def is_success_response(response: Response):
    SUCCESS_LIST = [
        HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT
    ]
    return response.status_code in SUCCESS_LIST