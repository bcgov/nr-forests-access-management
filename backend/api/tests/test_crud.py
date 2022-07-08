import pytest
import logging
import os

import api.app.crud as crud

LOGGER = logging.getLogger(__name__)

def test_getFamApplications(dbSession):
    # TODO: start coding tests for crud.py code.
    files = os.listdir('.')
    LOGGER.debug(f"files: {files}")

    famApps = crud.getFamApplications(dbSession)
    assert famApps == []
    LOGGER.debug(f'famApps: {famApps}')
    pass
