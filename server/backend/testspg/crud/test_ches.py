import logging
import time
from unittest.mock import MagicMock

import pytest
from api.app.integration.ches import ChesEmailService
from api.app.integration.ches.ches import CHES_API_BASE_URL
from api.app.schemas import GCNotifyGrantAccessEmailParamSchema
from api.app.schemas.fam_forest_client import FamForestClientSchema
from requests import HTTPError

LOGGER = logging.getLogger(__name__)

TEST_TOKEN_URL = "https://token.test/realms/comsvcauth/protocol/openid-connect/token"
EMAIL_MERGE_URL = f"{CHES_API_BASE_URL}/emailMerge"
DEFAULT_FROM = "Forest Access Management <do-not-reply-fam@gov.bc.ca>"


@pytest.fixture(autouse=True)
def ches_env(monkeypatch):
    """Provide the CHES config the service reads at construction time."""
    monkeypatch.setenv("CHES_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("CHES_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("CHES_TOKEN_URL", TEST_TOKEN_URL)
    # CHES_EMAIL_FROM intentionally left unset to exercise the default.


@pytest.fixture(autouse=True)
def reset_token_cache():
    """Token cache is class-level; reset it so tests don't leak state into each other."""
    ChesEmailService._access_token = None
    ChesEmailService._token_expiry = 0
    yield
    ChesEmailService._access_token = None
    ChesEmailService._token_expiry = 0


def _response(status_code=200, json_data=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data if json_data is not None else {}
    return resp


def _install_session(service, token_status=200, email_status=201, access_token="tok-123", expires_in=300):
    """Wire service.session.post to return canned token/email responses by URL."""
    def side_effect(url, *args, **kwargs):
        if url == TEST_TOKEN_URL:
            return _response(token_status, {"access_token": access_token, "expires_in": expires_in})
        if url == EMAIL_MERGE_URL:
            return _response(email_status, {"messages": [{"msgId": "abc-123"}]})
        return _response(404, {})

    service.session.post = MagicMock(side_effect=side_effect)
    return service.session.post


def _params(with_org=False, contact=None):
    org = (
        [
            FamForestClientSchema(
                client_name="CANADIAN FOREST PRODUCTS LTD.",
                forest_client_number="00001271",
            )
        ]
        if with_org
        else None
    )
    return GCNotifyGrantAccessEmailParamSchema(
        user_name="IANLIU",
        first_name="Ian",
        last_name="Liu",
        application_description="Waste Plus (TEST)",
        role_display_name="Viewer",
        organization_list=org,
        application_team_contact_email=contact,
        send_to_email="ian.liu@example.com",
    )


def _post_calls(post_mock, url):
    return [c for c in post_mock.call_args_list if c.args and c.args[0] == url]


class TestChesEmailService:
    def test_send_builds_emailmerge_payload(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_user_access_granted_email(_params())

        email_calls = _post_calls(post, EMAIL_MERGE_URL)
        assert len(email_calls) == 1
        payload = email_calls[0].kwargs["json"]
        assert payload["bodyType"] == "html"
        assert payload["encoding"] == "utf-8"
        assert payload["priority"] == "normal"
        assert payload["tag"]
        assert payload["from"] == DEFAULT_FROM
        assert payload["subject"] == "You have been granted access to Waste Plus (TEST)."
        assert payload["contexts"][0]["to"] == ["ian.liu@example.com"]

    def test_bearer_token_injected(self):
        service = ChesEmailService()
        post = _install_session(service, access_token="tok-abc")

        service.send_user_access_granted_email(_params())

        headers = _post_calls(post, EMAIL_MERGE_URL)[0].kwargs["headers"]
        assert headers["Authorization"] == "Bearer tok-abc"
        assert headers["Content-Type"] == "application/json"

    def test_context_without_organization(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_user_access_granted_email(_params(with_org=False))

        context = _post_calls(post, EMAIL_MERGE_URL)[0].kwargs["json"]["contexts"][0]["context"]
        assert context["organization_list"] == []
        assert context["application_name"] == "Waste Plus (TEST)"
        assert context["role_display_name"] == "Viewer"
        assert context["application_team_contact_email"] == ""

    def test_context_with_organization(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_user_access_granted_email(_params(with_org=True))

        context = _post_calls(post, EMAIL_MERGE_URL)[0].kwargs["json"]["contexts"][0]["context"]
        assert context["organization_list"] == [
            {"client_name": "CANADIAN FOREST PRODUCTS LTD.", "forest_client_number": "00001271"}
        ]

    def test_token_is_cached_across_instances(self):
        """A token is fetched once and reused for later sends, even by new instances."""
        service1 = ChesEmailService()
        post1 = _install_session(service1)
        service1.send_user_access_granted_email(_params())

        service2 = ChesEmailService()
        post2 = _install_session(service2)
        service2.send_user_access_granted_email(_params())

        # First instance fetched the token; second reused the class-level cache.
        assert len(_post_calls(post1, TEST_TOKEN_URL)) == 1
        assert len(_post_calls(post2, TEST_TOKEN_URL)) == 0
        assert len(_post_calls(post2, EMAIL_MERGE_URL)) == 1

    def test_token_refreshed_when_expired(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_user_access_granted_email(_params())
        # Force the cached token to look expired.
        ChesEmailService._token_expiry = time.time() - 1
        service.send_user_access_granted_email(_params())

        assert len(_post_calls(post, TEST_TOKEN_URL)) == 2

    def test_email_send_failure_raises(self):
        service = ChesEmailService()

        def side_effect(url, *args, **kwargs):
            if url == TEST_TOKEN_URL:
                return _response(200, {"access_token": "tok", "expires_in": 300})
            resp = _response(500, {})
            resp.raise_for_status.side_effect = HTTPError("500 Server Error")
            return resp

        service.session.post = MagicMock(side_effect=side_effect)

        with pytest.raises(HTTPError):
            service.send_user_access_granted_email(_params())

    def test_token_request_failure_raises(self):
        service = ChesEmailService()

        def side_effect(url, *args, **kwargs):
            resp = _response(401, {})
            resp.raise_for_status.side_effect = HTTPError("401 Unauthorized")
            return resp

        service.session.post = MagicMock(side_effect=side_effect)

        with pytest.raises(HTTPError):
            service.send_user_access_granted_email(_params())

    def test_invalid_email_address_rejected(self):
        """Param schema validates the recipient email before any send."""
        with pytest.raises(Exception) as excinfo:
            GCNotifyGrantAccessEmailParamSchema(
                user_name="IANLIU",
                application_description="fam",
                role_display_name="Viewer",
                send_to_email="not-an-email",
            )
        assert excinfo.match("value is not a valid email address")
