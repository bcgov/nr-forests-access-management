# flake8: ignore=F402

import os
import sys
import pytest
from fastapi.testclient import TestClient
import mock
from mock_alchemy.mocking import UnifiedAlchemyMagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.app.main import app
import api.app.dependencies as dependencies
from api.app.models import model as models


@pytest.fixture(scope="function")
def test_client_fixture() -> TestClient:

    app.dependency_overrides[dependencies.get_db] = override_get_db

    return TestClient(app)


def override_get_db():
    return UnifiedAlchemyMagicMock(data=[
        (
            [mock.call.query(models.FamApplication), mock.call.all()], []
        ),
    ])
