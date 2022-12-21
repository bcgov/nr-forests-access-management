# flake8: ignore=F402

import os
import sys
import pytest
from fastapi.testclient import TestClient
import mock
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from Crypto.PublicKey import RSA
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.app.main import app
import api.app.dependencies as dependencies
from api.app.models import model as models

# global placeholder to be populated by fixtures for JWT test
# sessions, required to override the get_drsa_key method.
public_rsa_key = None

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def test_client_fixture() -> TestClient:

    app.dependency_overrides[dependencies.get_db] = override_get_db

    return TestClient(app)


@pytest.fixture(scope="function")
def test_rsa_key() -> TestClient:

    new_key = RSA.generate(2048)
    global public_rsa_key
    public_rsa_key = new_key.publickey().exportKey("PEM")

    app.dependency_overrides[dependencies.get_rsa_key_method] = override_get_rsa_key_method

    return new_key.exportKey("PEM")


@pytest.fixture(scope="function")
def test_rsa_key_missing() -> TestClient:

    new_key = RSA.generate(2048)
    global public_rsa_key
    public_rsa_key = new_key.publickey().exportKey("PEM")

    app.dependency_overrides[dependencies.get_rsa_key_method] = override_get_rsa_key_method_none

    return new_key.exportKey("PEM")


def override_get_db():
    return UnifiedAlchemyMagicMock(data=[
        (
            [mock.call.query(models.FamApplication), mock.call.all()], []
        ),
    ])


def override_get_rsa_key_method():
    return override_get_rsa_key


def override_get_rsa_key(kid):
    global public_rsa_key
    return public_rsa_key


def override_get_rsa_key_method_none():
    return override_get_rsa_key_none


def override_get_rsa_key_none(kid):
    return None