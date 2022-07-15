import pytest
import logging
import os

import api.app.crud as crud

LOGGER = logging.getLogger(__name__)

def test_getFamApplications(dbSession):
    """Was a starting place to figure out crud tests that work with the database
    session, not complete.

    :param dbSession: _description_
    :type dbSession: _type_
    """
    # TODO: start coding tests for crud.py code.
    files = os.listdir('.')
    LOGGER.debug(f"files: {files}")

    famApps = crud.getFamApplications(dbSession)
    assert famApps == []
    LOGGER.debug(f'famApps: {famApps}')

    # add an app and verify its returned.
    pass

def test_getFamUsers(dbSession):
    pass
