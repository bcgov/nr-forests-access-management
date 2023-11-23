import logging
import pytest
from pydantic import ValidationError
from fastapi import HTTPException

from api.app import schemas

from tests.constants import (
    TEST_NEW_APPLICATION_ADMIN,
    TEST_CREATOR,
    TEST_NOT_INVALID_USER_TYPE,
)


LOGGER = logging.getLogger(__name__)


# def test_create_application_admin():
#     access_roles_fam_only = ["FAM_ACCESS_ADMIN"]
#     token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fam_only)
#     response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["application_name"] == "FAM"