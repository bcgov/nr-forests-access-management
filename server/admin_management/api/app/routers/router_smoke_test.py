import logging

from fastapi import APIRouter

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", status_code=200)
def smoke_test():
    try:
        return {"greeting": "Hello world"}

    except Exception as e:
        LOGGER.exception(e)
        raise e
