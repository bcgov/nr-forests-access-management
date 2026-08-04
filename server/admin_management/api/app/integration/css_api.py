import logging
import time
from http import HTTPStatus
from urllib.parse import quote
from typing import List

import requests
from api.app.schemas.css_integration import (CssIntegrationSchema,
                                             CssRoleSchema)
from api.config import config

LOGGER = logging.getLogger(__name__)


class CssApiService:
    """
    Client for the BC Gov Common Hosted Single Sign-On (CSS) API.

    Proof of concept for sourcing applications from CSS integrations instead of
    the fam_application table. See .ai/keycloak-css-feasibility.md

    A CSS integration spans environments - the environments are returned as an
    array on the integration, and the role endpoints take the environment as a
    path segment (/integrations/{id}/{env}/roles). So one integration maps onto
    several FAM "application per environment" rows.
    """

    TIMEOUT = (5, 10)  # (connect, read) in seconds

    # CSS API accounts authenticate with client_credentials. Tokens are cached on
    # the class so a burst of requests does not mint one each time; refreshed a
    # little early to avoid using a token that expires mid-flight.
    _token: str | None = None
    _token_expires_at: float = 0.0
    TOKEN_EXPIRY_BUFFER_SECONDS = 30

    def __init__(self):
        self.api_base_url = config.get_css_api_baseurl()
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _get_token(self) -> str:
        now = time.time()
        if CssApiService._token and now < CssApiService._token_expires_at:
            return CssApiService._token

        LOGGER.debug("CssApiService: requesting a new access token")
        response = requests.post(
            config.get_css_token_url(),
            data={
                "grant_type": "client_credentials",
                "client_id": config.get_css_client_id(),
                "client_secret": config.get_css_client_secret(),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        CssApiService._token = payload["access_token"]
        CssApiService._token_expires_at = (
            now + payload.get("expires_in", 300) - self.TOKEN_EXPIRY_BUFFER_SECONDS
        )
        return CssApiService._token

    def get_integrations(self) -> List[CssIntegrationSchema]:
        """
        List the integrations owned by the CSS team this API account belongs to.

        Note the account is team scoped: this returns every integration under the
        team, with no per-user filtering. FAM's own admin tables remain the source
        of truth for which applications a given requester may administer.
        """
        url = f"{self.api_base_url}/integrations"
        LOGGER.debug(f"CssApiService.get_integrations() - url: {url}")

        response = self.session.get(
            url,
            headers={"Authorization": f"Bearer {self._get_token()}"},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()

        integrations = [
            CssIntegrationSchema(**item) for item in response.json().get("data", [])
        ]
        LOGGER.debug(f"CssApiService.get_integrations() - {len(integrations)} found")
        return integrations

    def get_roles(self, integration_id: int, environment: str) -> List[CssRoleSchema]:
        """
        Roles defined on an integration, for one environment.

        CSS roles carry a name and a `composite` flag and nothing else - no
        display name, no description, no attributes. Callers wanting anything
        human readable have to source it elsewhere.
        """
        url = f"{self.api_base_url}/integrations/{integration_id}/{environment}/roles"
        LOGGER.debug(f"CssApiService.get_roles() - url: {url}")

        response = self.session.get(
            url,
            headers={"Authorization": f"Bearer {self._get_token()}"},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return [CssRoleSchema(**item) for item in response.json().get("data", [])]

    def get_role_composites(
        self, integration_id: int, environment: str, role_name: str
    ) -> List[str]:
        """
        The child roles of a composite role.

        FAM uses these as scope-type markers: a role composed of
        HAS_DISTRICT_ROLE is district scoped, one composed of HAS_FOREST_CLIENT
        is forest client scoped. That is the only way to express scope type in
        CSS, which has no role attributes.
        """
        url = (
            f"{self.api_base_url}/integrations/{integration_id}/{environment}"
            f"/roles/{role_name}/composite-roles"
        )
        response = self.session.get(
            url,
            headers={"Authorization": f"Bearer {self._get_token()}"},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return [item["name"] for item in response.json().get("data", [])]

    def create_role(self, integration_id: int, environment: str, role_name: str) -> None:
        """
        Create a role. CSS accepts only a name - there is nowhere to put a
        description or any attribute.

        Treated as find-or-create: a 409 means another request created it first,
        which is the desired end state either way.
        """
        url = f"{self.api_base_url}/integrations/{integration_id}/{environment}/roles"
        LOGGER.debug(f"CssApiService.create_role() - {role_name}")

        response = self.session.post(
            url,
            headers={"Authorization": f"Bearer {self._get_token()}"},
            json={"name": role_name},
            timeout=self.TIMEOUT,
        )
        if response.status_code == HTTPStatus.CONFLICT:
            LOGGER.debug(f"CssApiService.create_role() - {role_name} already exists")
            return
        response.raise_for_status()

    def assign_user_roles(
        self, integration_id: int, environment: str, username: str, role_names: List[str]
    ) -> None:
        """
        Assign roles to a user. `username` is the CSS/Keycloak username, not a FAM
        user name - see build_css_username().
        """
        url = (
            f"{self.api_base_url}/integrations/{integration_id}/{environment}"
            f"/users/{username}/roles"
        )
        LOGGER.debug(f"CssApiService.assign_user_roles() - {username} -> {role_names}")

        response = self.session.post(
            url,
            headers={"Authorization": f"Bearer {self._get_token()}"},
            json=[{"name": name} for name in role_names],
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()

    def get_users_with_role(
        self, integration_id: int, environment: str, role_name: str
    ) -> List[dict]:
        """
        Users holding one role.

        The only way CSS exposes assignments - there is no endpoint listing every
        user in an integration, and /user-role-mappings returns 404 for every role
        we have tried, so callers must fan out over roles and merge.
        """
        url = (
            f"{self.api_base_url}/integrations/{integration_id}/{environment}"
            f"/roles/{quote(role_name, safe='')}/users"
        )
        response = self.session.get(
            url,
            headers={"Authorization": f"Bearer {self._get_token()}"},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("data", []) or []
