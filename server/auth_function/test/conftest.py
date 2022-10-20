import pytest
import logging
import sys
import os

modulePath = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(modulePath)
import lambda_function




LOGGER = logging.getLogger(__name__)

#server/auth_function/test/database_setup_fixtures.py
pytest_plugins = [
    "database_setup_fixtures"
]

