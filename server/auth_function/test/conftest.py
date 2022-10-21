import logging
import sys
import os

modulePath = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(modulePath)
import lambda_function  # noqa - need import here to make avail to fixtures/tests

LOGGER = logging.getLogger(__name__)

pytest_plugins = ["database_setup_fixtures"]
