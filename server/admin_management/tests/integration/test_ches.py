import logging
import time
from unittest.mock import MagicMock

import pytest
from api.app.integration.ches import ChesEmailService
from api.app.integration.ches.ches import CHES_API_BASE_URL, TC_FILENAME
from api.app.schemas.schemas import (FamForestClientBase,
                                     GCNotifyGrantDelegatedAdminEmailParam)
from requests import HTTPError

LOGGER = logging.getLogger(__name__)

TEST_TOKEN_URL = "https://token.test/realms/comsvcauth/protocol/openid-connect/token"
EMAIL_MERGE_URL = f"{CHES_API_BASE_URL}/emailMerge"
DEFAULT_FROM = "Forest Access Management <do-not-reply-fam@gov.bc.ca>"
# is_on_aws() is False in tests, so the service uses the dev frontend url.
FRONTEND_URL = "https://fam-dev.nrs.gov.bc.ca"


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


def _install_session(service, access_token="tok-123", expires_in=300):
    def side_effect(url, *args, **kwargs):
        if url == TEST_TOKEN_URL:
            return _response(200, {"access_token": access_token, "expires_in": expires_in})
        if url == EMAIL_MERGE_URL:
            return _response(201, {"messages": [{"msgId": "abc-123"}]})
        return _response(404, {})

    service.session.post = MagicMock(side_effect=side_effect)
    return service.session.post


def _params(with_org=False, is_bceid=False, contact=None):
    org = (
        [
            FamForestClientBase(
                client_name="CANADIAN FOREST PRODUCTS LTD.",
                forest_client_number="00001271",
            )
        ]
        if with_org
        else None
    )
    return GCNotifyGrantDelegatedAdminEmailParam(
        send_to_email_address="ian.liu@example.com",
        user_name="IANLIU",
        first_name="Ian",
        last_name="Liu",
        application_description="Interior Logging Cost Reporting Application (TEST)",
        role_display_name="Admin",
        organization_list=org,
        application_team_contact_email=contact,
        is_bceid_user="yes" if is_bceid else "no",
    )


def _post_calls(post_mock, url):
    return [c for c in post_mock.call_args_list if c.args and c.args[0] == url]


def _email_context(post_mock):
    return _post_calls(post_mock, EMAIL_MERGE_URL)[0].kwargs["json"]["contexts"][0]["context"]


class TestChesEmailService:
    def test_send_builds_emailmerge_payload(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_delegated_admin_granted_email(_params())

        email_calls = _post_calls(post, EMAIL_MERGE_URL)
        assert len(email_calls) == 1
        payload = email_calls[0].kwargs["json"]
        assert payload["bodyType"] == "html"
        assert payload["encoding"] == "utf-8"
        assert payload["from"] == DEFAULT_FROM
        assert payload["subject"] == (
            "You have been assigned as a delegated administrator role for "
            "Interior Logging Cost Reporting Application (TEST)."
        )
        assert payload["contexts"][0]["to"] == ["ian.liu@example.com"]

    def test_bearer_token_injected(self):
        service = ChesEmailService()
        post = _install_session(service, access_token="tok-abc")

        service.send_delegated_admin_granted_email(_params())

        headers = _post_calls(post, EMAIL_MERGE_URL)[0].kwargs["headers"]
        assert headers["Authorization"] == "Bearer tok-abc"

    def test_context_bceid_user_gets_tc_link(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_delegated_admin_granted_email(_params(is_bceid=True))

        context = _email_context(post)
        assert context["is_bceid_user"] is True
        assert context["login_url"] == FRONTEND_URL
        assert context["terms_conditions_url"] == f"{FRONTEND_URL}/{TC_FILENAME}"

    def test_context_non_bceid_user_no_tc(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_delegated_admin_granted_email(_params(is_bceid=False))

        assert _email_context(post)["is_bceid_user"] is False

    def test_context_without_organization(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_delegated_admin_granted_email(_params(with_org=False))

        context = _email_context(post)
        assert context["organization_list"] == []
        assert context["role_display_name"] == "Admin"
        assert context["application_team_contact_email"] == ""

    def test_context_with_organization(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_delegated_admin_granted_email(_params(with_org=True))

        assert _email_context(post)["organization_list"] == [
            {"client_name": "CANADIAN FOREST PRODUCTS LTD.", "forest_client_number": "00001271"}
        ]

    def test_token_is_cached_across_instances(self):
        service1 = ChesEmailService()
        post1 = _install_session(service1)
        service1.send_delegated_admin_granted_email(_params())

        service2 = ChesEmailService()
        post2 = _install_session(service2)
        service2.send_delegated_admin_granted_email(_params())

        assert len(_post_calls(post1, TEST_TOKEN_URL)) == 1
        assert len(_post_calls(post2, TEST_TOKEN_URL)) == 0
        assert len(_post_calls(post2, EMAIL_MERGE_URL)) == 1

    def test_token_refreshed_when_expired(self):
        service = ChesEmailService()
        post = _install_session(service)

        service.send_delegated_admin_granted_email(_params())
        ChesEmailService._token_expiry = time.time() - 1
        service.send_delegated_admin_granted_email(_params())

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
            service.send_delegated_admin_granted_email(_params())

    def test_token_request_failure_raises(self):
        service = ChesEmailService()

        def side_effect(url, *args, **kwargs):
            resp = _response(401, {})
            resp.raise_for_status.side_effect = HTTPError("401 Unauthorized")
            return resp

        service.session.post = MagicMock(side_effect=side_effect)

        with pytest.raises(HTTPError):
            service.send_delegated_admin_granted_email(_params())
