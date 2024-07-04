import json
import logging
from http import HTTPStatus

from api.app.constants import ERROR_CODE_INVALID_OPERATION
from fastapi import HTTPException

LOGGER = logging.getLogger(__name__)


def read_json_file(file_path):
    with open(file_path, 'r') as myfile:
        data = myfile.read()

    # parse file
    obj = json.loads(data)
    return obj


def raise_http_exception(
    error_msg: str,
    error_code: str = ERROR_CODE_INVALID_OPERATION,  # default, please override if necessary
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST,  # default http status, please override if necessary
):
    LOGGER.debug(f"raise_http_exception: {error_msg}")
    raise HTTPException(
        status_code=status_code,
        detail={
            "code": error_code,
            "description": error_msg,
        }
    )
