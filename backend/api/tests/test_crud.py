import pytest
import logging
import os

LOGGER = logging.getLogger(__name__)

def test_getFamApplications(dbSession):
    # TODO: start coding tests for crud.py code.
    files = os.listdir('.')
    LOGGER.debug(f"files: {files}")
    pass
