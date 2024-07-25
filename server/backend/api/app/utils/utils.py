import base64
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


# This is util function to add padding (for base64.urlsafe_b64decode to work)
# https://stackoverflow.com/questions/3302946/how-to-decode-base64-url-in-python
def base64url_decode(input):
    """Helper method to base64url_decode a string.

    Args:
        input (str): A base64url_encoded string to decode.

    """
    rem = len(input) % 4

    if rem > 0:
        input += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(input)


def ensure_binary(s):
    """Coerce **s** to bytes."""

    if isinstance(s, bytes):
        return s
    if isinstance(s, str):
        return s.encode("utf-8", "strict")
    raise TypeError(f"not expecting type '{type(s)}'")