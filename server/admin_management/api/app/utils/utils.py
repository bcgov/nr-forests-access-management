import logging
from fastapi import HTTPException

LOGGER = logging.getLogger(__name__)


def raise_http_exception(status_code: str, error_msg: str):
    LOGGER.info(error_msg)
    raise HTTPException(status_code=status_code, detail=error_msg)

def construct_forest_client_role_name(
    parent_role_name: str, forest_client_number: str
):
    return f"{parent_role_name}_{forest_client_number}"

def construct_forest_client_role_purpose(
    parent_role_purpose: str, forest_client_number: str
):
    client_purpose = f"{parent_role_purpose} for {forest_client_number}"
    return client_purpose