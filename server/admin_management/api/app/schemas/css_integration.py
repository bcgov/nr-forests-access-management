from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CssIntegrationSchema(BaseModel):
    """
    A CSS integration, as returned by GET /integrations.

    Field names mirror the CSS API response. Note `environments` is an array -
    one integration spans dev/test/prod - which is why it does not map one to one
    onto a FAM application row.
    """

    id: int
    projectName: str
    authType: Optional[str] = None
    environments: List[str] = []
    status: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CssApplicationOptionSchema(BaseModel):
    """
    One selectable application in the FAM admin UI, derived from a CSS integration
    by fanning out its `environments` array.

    A CSS integration "Forest and Range Evaluation Program" with
    environments ["dev", "test"] produces two options.
    """

    integration_id: int
    environment: str
    name: str
    description: str
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CssRoleSchema(BaseModel):
    """A role as CSS returns it: a name and a composite flag, nothing more."""

    name: str
    composite: bool = False

    model_config = ConfigDict(from_attributes=True)


# Marker roles used to express scope type, since CSS roles cannot carry attributes.
# A role composed of one of these is scoped by that dimension.
CSS_MARKER_DISTRICT = "HAS_DISTRICT_ROLE"
CSS_MARKER_FOREST_CLIENT = "HAS_FOREST_CLIENT"


class CssRoleOptionSchema(BaseModel):
    """
    One selectable role in the FAM admin UI, sourced from CSS.

    CSS roles cannot carry a display name, so the convention is to nest them:
    a human readable role composed of the machine role code, which in turn may be
    composed of scope markers.

        Submitter (CHR)  ->  CHR_FREP_EDITOR  ->  HAS_DISTRICT_ROLE
        Submitter (SLR)  ->  FREP_EDITOR
        Administrator    ->  FREP_ADMINISTRATOR

    `display_name` is the outermost (human readable) role, `role_code` the machine
    role beneath it, and the scope flags are resolved by walking the whole chain.

    `description` stays None - there is nowhere in CSS to put one.
    """

    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    role_code: Optional[str] = None
    composite: bool = False
    composites: List[str] = []
    role_type_district: bool = False
    role_type_client: bool = False

    model_config = ConfigDict(from_attributes=True)


def build_scoped_role_name(base_role_name: str, scope_type: str, scope_value: str) -> str:
    """
    Name for a scope-specific role created on demand at grant time.

        CHR_FREP_EDITOR + DISTRICT + DCC  ->  CHR_FREP_EDITOR_DISTRICT-DCC

    The scope type and value travel in the role name because that is the only
    place CSS can carry them - a role has no attributes, and the name is what
    reaches the token in the client_roles claim.
    """
    return f"{base_role_name}_{scope_type}-{scope_value}"


def build_css_username(user_guid: str, user_type_code: str) -> str:
    """
    CSS/Keycloak username for a FAM user.

    Keycloak identifies federated users as <guid>@<idp>, lower case, e.g.
    5029b0d70ae24dd39d64a2ca10bfba59@idir. FAM stores user_guid upper case, so it
    is lowered here.
    """
    idp = {"I": "idir", "B": "bceidbusiness"}.get(user_type_code)
    if not idp:
        raise ValueError(f"No CSS identity provider mapping for user type {user_type_code}")
    return f"{user_guid.lower()}@{idp}"


class CssUserRoleAssignmentRequest(BaseModel):
    """A grant of one role, optionally scoped, to one user."""

    user_guid: str
    user_type_code: str
    role_name: str
    scope_type: Optional[str] = None
    scope_values: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class CssUserRoleAssignmentResult(BaseModel):
    """Outcome per role actually assigned."""

    role_name: str
    role_created: bool = False
    assigned: bool = False
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CssUserRoleRowSchema(BaseModel):
    """
    One user's assignment of one role, for the permissions table.

    Assembled by fanning out over every role in the integration - CSS has no
    "all users in this integration" endpoint, only GET /roles/{name}/users.

    Several columns FAM shows have no CSS source: there is no granted-on date, no
    expiry, and no forest client / organization. Those come back None.
    """

    username: str
    domain: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    role_name: str
    scope_type: Optional[str] = None
    scope_value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


def parse_scoped_role_name(role_name: str):
    """
    Split a generated role name back into its parts.

        CHR_FREP_EDITOR_DISTRICT-DCC  ->  ('CHR_FREP_EDITOR', 'DISTRICT', 'DCC')
        FREP_EDITOR                   ->  ('FREP_EDITOR', None, None)

    The scope only exists in the name, so this is the only way to recover it.
    """
    base, sep, tail = role_name.rpartition("-")
    if not sep or "_" not in base:
        return role_name, None, None
    prefix, _, scope_type = base.rpartition("_")
    if not prefix:
        return role_name, None, None
    return prefix, scope_type, tail


def domain_from_css_username(username: str) -> Optional[str]:
    """'<guid>@idir' -> 'IDIR'. Returns None when there is no recognisable suffix."""
    _, _, idp = username.partition("@")
    return {
        "idir": "IDIR",
        "azureidir": "IDIR",
        "bceidbusiness": "BCEID",
    }.get(idp.lower())
