import logging
import time
from pathlib import Path

import requests
from api.app.schemas.schemas import GCNotifyGrantDelegatedAdminEmailParam
from api.app.utils.utils import is_success_response
from api.config import config
from requests.auth import HTTPBasicAuth

LOGGER = logging.getLogger(__name__)

# CHES (Common Hosted Email Service) public API gateway. Same host for all
# environments; the environment is determined by which token endpoint / client
# credentials are used (see config.get_ches_token_url).
CHES_API_BASE_URL = "https://ches.api.gov.bc.ca/api/v1"

# Refresh the OAuth token slightly before it actually expires to avoid using a
# token that lapses mid-request.
TOKEN_EXPIRY_MARGIN_SECONDS = 30

# Current FAM Terms-and-Conditions file, deposited under the frontend /public
# folder with a url-friendly name. See TermsAndConditions.vue / release notes when
# the version changes (must be updated in both frontend and here).
TC_FILENAME = "2024-06-04-fam-terms-conditions.pdf"

# Templates are owned by FAM (CHES has no hosted templates). Rendered server-side
# by CHES via nunjucks when posted to /emailMerge.
_TEMPLATE_DIR = Path(__file__).parent / "email_templates"


class ChesEmailService:
    """
    Sends email through BC Gov CHES (Common Hosted Email Service).

    Auth is OAuth2 client-credentials (Keycloak): a bearer token is fetched and
    injected on every request. Email bodies are FAM-owned nunjucks templates sent
    to the CHES /emailMerge endpoint with a per-recipient context of substitution
    variables.
    """

    TIMEOUT = (5, 10)  # Timeout (connect, read) in seconds.

    _access_token = None
    _token_expiry = 0  # epoch seconds; 0 forces an initial fetch.

    def __init__(self):
        self.client_id = config.get_ches_client_id()
        self.client_secret = config.get_ches_client_secret()
        self.token_url = config.get_ches_token_url()
        self.email_from = config.get_ches_email_from()
        self.api_base_url = CHES_API_BASE_URL

        self.session = requests.Session()

    # ------------------------------- Auth ------------------------------- #

    def _get_token(self) -> str:
        """
        Return a valid OAuth2 access token, fetching a new one (client-credentials
        grant) when there is no cached token or the cached one is about to expire.
        """
        now = time.time()
        if ChesEmailService._access_token and now < ChesEmailService._token_expiry:
            return ChesEmailService._access_token

        r = self.session.post(
            self.token_url,
            timeout=self.TIMEOUT,
            data={"grant_type": "client_credentials"},
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
        )
        if not is_success_response(r):
            LOGGER.debug(f"CHES token request failed: {r.__dict__}")
            r.raise_for_status()

        token_data = r.json()
        ChesEmailService._access_token = token_data["access_token"]
        # expires_in is seconds from now; keep a safety margin.
        ChesEmailService._token_expiry = (
            now + token_data.get("expires_in", 0) - TOKEN_EXPIRY_MARGIN_SECONDS
        )
        return ChesEmailService._access_token

    def _auth_header(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    # ---------------------------- Public API ---------------------------- #

    def send_delegated_admin_granted_email(
        self, params: GCNotifyGrantDelegatedAdminEmailParam
    ):
        """
        Send the 'delegated admin granted' email for a new delegated administrator.
        """
        # Environment-correct frontend url for the login link and (BCeID-only)
        # terms-and-conditions link. Mirrors the previous GC Notify logic.
        frontend_url = (
            config.get_env_var("ALLOW_ORIGIN")
            if config.is_on_aws()
            else "https://fam-dev.nrs.gov.bc.ca"
        )

        context = {
            "user_name": params.user_name,
            "first_name": params.first_name,
            "last_name": params.last_name,
            "application_name": params.application_description,
            "role_display_name": params.role_display_name,
            # Structured list; the template loops/formats it (nunjucks {% for %}).
            "organization_list": [
                {
                    "client_name": item.client_name,
                    "forest_client_number": item.forest_client_number,
                }
                for item in (params.organization_list or [])
            ],
            "application_team_contact_email": params.application_team_contact_email or "",
            # T&C block is shown for BCeID users only.
            "is_bceid_user": params.is_bceid_user == "yes",
            "login_url": frontend_url,
            "terms_conditions_url": f"{frontend_url}/{TC_FILENAME}",
        }
        subject = (
            f"You have been assigned as a delegated administrator role for "
            f"{params.application_description}."
        )

        return self._send_merge(
            template_name="grant_delegated_admin.html",
            subject=subject,
            to=[params.send_to_email_address],
            context=context,
        )

    # ---------------------------- Internal ------------------------------ #

    def _send_merge(self, template_name: str, subject: str, to: list, context: dict):
        """
        POST a templated email to the CHES /emailMerge endpoint. CHES renders the
        nunjucks `body` against each entry's `context` and sends one email per entry.
        """
        body = self._load_template(template_name)
        email_params = {
            "bodyType": "html",
            "body": body,
            "subject": subject,
            "from": self.email_from,
            "encoding": "utf-8",
            "priority": "normal",
            "tag": "fam-grant-delegated-admin",
            "contexts": [
                {
                    "to": to,
                    "context": context,
                }
            ],
        }
        LOGGER.debug(f"Sending CHES email with param {email_params}")
        send_url = f"{self.api_base_url}/emailMerge"

        r = self.session.post(
            send_url, timeout=self.TIMEOUT, headers=self._auth_header(), json=email_params
        )

        if not is_success_response(r):
            LOGGER.debug(f"Email sending response: {r.__dict__}")
            r.raise_for_status()

        send_email_result = r.json()
        LOGGER.debug(f"Email sending result: {send_email_result}")
        return send_email_result

    @staticmethod
    def _load_template(template_name: str) -> str:
        return (_TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
