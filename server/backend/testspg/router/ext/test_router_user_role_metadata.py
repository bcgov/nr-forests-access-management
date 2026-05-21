from datetime import datetime, timezone
from http.client import FORBIDDEN
import json
import logging
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from api.app.constants import (ERROR_CODE_INVALID_OPERATION,
                               ERROR_CODE_REQUESTER_NOT_EXISTS, UserType)
from api.app.crud import crud_application, crud_user_role
from api.app.jwt_validation import ERROR_EXPIRED_TOKEN
from api.app.main import external_v1_api_prefix
from fastapi import status
from fastapi.testclient import TestClient
from testspg import jwt_utils

LOGGER = logging.getLogger(__name__)
end_point = f"{external_v1_api_prefix}/users/me/role-metadata"

def _build_assignment(
    role_name: str,
    display_name: str,
    expiry_date: datetime | None,
    forest_client_number: str | None = None,
):
    forest_client_relation = None
    if forest_client_number is not None:
        forest_client_relation = SimpleNamespace(
            forest_client_number=forest_client_number
        )

    role = SimpleNamespace(
        role_name=role_name,
        display_name=display_name,
        forest_client_relation=forest_client_relation,
    )
    return SimpleNamespace(role=role, expiry_date=expiry_date)


def test_user_role_metadata_bearer_token_required(
    test_client_fixture: TestClient,
):
    response = test_client_fixture.get(end_point)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_role_metadata_expired_token(
    test_client_fixture: TestClient,
    test_rsa_key,
):
    claims = jwt_utils.create_jwt_claims()
    claims["exp"] = datetime.now(timezone.utc).timestamp() - 1000
    token = jwt_utils.create_jwt_token(test_rsa_key, claims=claims)

    response = test_client_fixture.get(end_point, headers=jwt_utils.headers(token))
    jwt_utils.assert_error_response(
        response, status.HTTP_401_UNAUTHORIZED, ERROR_EXPIRED_TOKEN
    )


def test_user_role_metadata_requester_not_exists(
    test_client_fixture: TestClient,
    test_rsa_key,
):
    claims = jwt_utils.create_jwt_claims()
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        username="missing-user-for-role-metadata@idir",
        claims=claims,
    )

    response = test_client_fixture.get(end_point, headers=jwt_utils.headers(token))
    jwt_utils.assert_error_response(
        response,
        FORBIDDEN,
        ERROR_CODE_REQUESTER_NOT_EXISTS,
    )


def test_user_role_metadata_invalid_app_client_id(
    test_client_fixture: TestClient,
    auth_headers,
    override_depends__get_current_requester,
):
    override_depends__get_current_requester()

    with patch.object(
        crud_application, "get_application_by_app_client_id", return_value=None
    ):
        response = test_client_fixture.get(end_point, headers=auth_headers)

    jwt_utils.assert_error_response(
        response,
        FORBIDDEN,
        ERROR_CODE_INVALID_OPERATION,
    )

    error_msg = json.loads(response.text)["detail"]["description"]
    assert "Token contains invalid application client id" in error_msg


def test_user_role_metadata_empty_roles(
    test_client_fixture: TestClient,
    auth_headers,
    override_depends__get_current_requester,
):
    requester = {
        "cognito_user_id": "test-idir-role-metadata-empty@idir",
        "user_name": "TEST_EMPTY",
        "user_type_code": UserType.IDIR,
        "user_id": 101,
        "user_guid": "12345678901234567890123456789012",
    }
    override_depends__get_current_requester(requester)

    mock_app = MagicMock()
    mock_app.application_id = 2

    with patch.object(
        crud_application,
        "get_application_by_app_client_id",
        return_value=mock_app,
    ), patch.object(
        crud_user_role,
        "get_user_roles_by_cognito_id_and_app_id",
        return_value=[],
    ):
        response = test_client_fixture.get(end_point, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "user_name": "TEST_EMPTY",
        "domain": "IDIR",
        "roles": [],
    }


def test_user_role_metadata_roles_with_expiry_and_forest_client(
    test_client_fixture: TestClient,
    auth_headers,
    override_depends__get_current_requester,
):
    requester = {
        "cognito_user_id": "test-bceid-role-metadata@bceidbusiness",
        "user_name": "TEST_ROLE_USER",
        "user_type_code": UserType.BCEID,
        "user_id": 102,
        "user_guid": "22345678901234567890123456789012",
    }
    override_depends__get_current_requester(requester)

    mock_app = MagicMock()
    mock_app.application_id = 2

    # Define assignment objects as variables
    submitter_assignment = _build_assignment(
        role_name="FOM_SUBMITTER_00001011",
        display_name="Submitter",
        expiry_date=datetime.now(timezone.utc).replace(year=datetime.now(timezone.utc).year + 2),
        forest_client_number="00001011",
    )

    reviewer_assignment = _build_assignment(
        role_name="FOM_REVIEWER",
        display_name="Reviewer",
        expiry_date=None,
        forest_client_number=None,
    )

    editor_assignment = _build_assignment(
        role_name="FOM_EDITOR",
        display_name="Editor",
        expiry_date=datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        forest_client_number=None,
    )

    assignments = [
        submitter_assignment,
        reviewer_assignment,
        editor_assignment,
    ]

    with patch.object(
        crud_application,
        "get_application_by_app_client_id",
        return_value=mock_app,
    ), patch.object(
        crud_user_role,
        "get_user_roles_by_cognito_id_and_app_id",
        return_value=assignments,
    ):
        response = test_client_fixture.get(end_point, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["user_name"] == "TEST_ROLE_USER"
    assert body["domain"] == "BCEID"
    assert len(body["roles"]) == 3

    assert body["roles"][0] == {
        "role_name": submitter_assignment.role.role_name,
        "display_name": submitter_assignment.role.display_name,
        "expiry_date": submitter_assignment.expiry_date.replace(microsecond=0).isoformat().replace("+00:00", "Z") if submitter_assignment.expiry_date else None,
        "forest_client_number": submitter_assignment.role.forest_client_relation.forest_client_number if submitter_assignment.role.forest_client_relation else None,
    }
    assert body["roles"][1] == {
        "role_name": reviewer_assignment.role.role_name,
        "display_name": reviewer_assignment.role.display_name,
        "expiry_date": reviewer_assignment.expiry_date.replace(microsecond=0).isoformat().replace("+00:00", "Z") if reviewer_assignment.expiry_date else None,
        "forest_client_number": reviewer_assignment.role.forest_client_relation.forest_client_number if reviewer_assignment.role.forest_client_relation else None,
    }
    assert body["roles"][2] == {
        "role_name": editor_assignment.role.role_name,
        "display_name": editor_assignment.role.display_name,
        "expiry_date": editor_assignment.expiry_date.replace(microsecond=0).isoformat().replace("+00:00", "Z") if editor_assignment.expiry_date else None,
        "forest_client_number": editor_assignment.role.forest_client_relation.forest_client_number if editor_assignment.role.forest_client_relation else None,
    }
