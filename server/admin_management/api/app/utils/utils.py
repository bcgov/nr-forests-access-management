import logging
from fastapi import HTTPException

LOGGER = logging.getLogger(__name__)


def raise_http_exception(status_code: str, error_msg: str):
    LOGGER.info(error_msg)
    raise HTTPException(status_code=status_code, detail=error_msg)
