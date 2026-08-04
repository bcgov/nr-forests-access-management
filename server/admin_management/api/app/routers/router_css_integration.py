import logging
from typing import List

from api.app import jwt_validation
from api.app.integration.css_api import CssApiService
from api.app.schemas.css_integration import (CSS_MARKER_DISTRICT,
                                             CSS_MARKER_FOREST_CLIENT,
                                             CssApplicationOptionSchema,
                                             CssRoleOptionSchema,
                                             CssUserRoleAssignmentRequest,
                                             CssUserRoleAssignmentResult,
                                             CssUserRoleRowSchema,
                                             build_css_username,
                                             build_scoped_role_name,
                                             domain_from_css_username,
                                             parse_scoped_role_name)
from fastapi import APIRouter, Depends

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=List[CssApplicationOptionSchema],
    dependencies=[Depends(jwt_validation.authorize)],
)
def get_css_applications():
    """
    Applications available to administer, sourced from CSS integrations instead of
    the fam_application table.

    Each CSS integration is fanned out over its `environments` array, so
    "Forest and Range Evaluation Program" with environments ["dev", "test"]
    yields two options - matching FAM's one-row-per-environment model.

    Caveat: a CSS API account is team scoped, so this returns every integration the
    team owns with no per-requester filtering. FAM's fam_application_admin and
    fam_access_control_privilege tables remain the authority on which applications
    a given requester may administer.

    See .ai/keycloak-css-feasibility.md
    """
    integrations = CssApiService().get_integrations()

    options = [
        CssApplicationOptionSchema(
            integration_id=integration.id,
            environment=environment,
            name=integration.projectName,
            description=f"{integration.projectName} ({environment.upper()})",
            status=integration.status,
        )
        for integration in integrations
        for environment in integration.environments
    ]

    LOGGER.debug(
        f"Returning {len(options)} application option(s) "
        f"from {len(integrations)} CSS integration(s)."
    )
    return options


@router.get(
    "/{integration_id}/{environment}/roles",
    response_model=List[CssRoleOptionSchema],
    dependencies=[Depends(jwt_validation.authorize)],
)
def get_css_application_roles(integration_id: int, environment: str):
    """
    Selectable roles for one CSS integration + environment.

    CSS roles hold only a name - no display name, no description, no attributes -
    so meaning is expressed by nesting roles as composites:

        Submitter (CHR)  ->  CHR_FREP_EDITOR  ->  HAS_DISTRICT_ROLE
        Submitter (SLR)  ->  FREP_EDITOR
        Administrator    ->  FREP_ADMINISTRATOR

    A role is selectable when nothing else composes it - i.e. it sits at the top of
    its chain. That is what makes "Submitter (SLR)" a row while its child
    FREP_EDITOR is not, without relying on a naming convention.

    Scope type is resolved by walking the whole chain for marker roles, so
    "Submitter (CHR)" is district scoped via its grandchild HAS_DISTRICT_ROLE.

    Cost: one composite lookup per composite role, since GET /roles already reports
    the composite flag for leaves.
    """
    css = CssApiService()
    roles = css.get_roles(integration_id, environment)
    markers = {CSS_MARKER_DISTRICT, CSS_MARKER_FOREST_CLIENT}

    # Full composite graph. Leaves are skipped - GET /roles already told us.
    composites_of: dict[str, List[str]] = {
        role.name: (
            css.get_role_composites(integration_id, environment, role.name)
            if role.composite
            else []
        )
        for role in roles
    }

    # A role composed by something else is an implementation detail of that
    # something else, not a row of its own.
    composed_by_others = {
        child for children in composites_of.values() for child in children
    }

    def walk(role_name: str, seen: set) -> List[str]:
        """Every descendant of role_name, guarding against a cyclic definition."""
        if role_name in seen:
            return []
        seen.add(role_name)
        descendants: List[str] = []
        for child in composites_of.get(role_name, []):
            descendants.append(child)
            descendants.extend(walk(child, seen))
        return descendants

    options: List[CssRoleOptionSchema] = []
    for role in roles:
        if role.name in markers or role.name in composed_by_others:
            continue

        chain = walk(role.name, set())
        role_code = next((name for name in chain if name not in markers), None)

        options.append(
            CssRoleOptionSchema(
                name=role.name,
                display_name=role.name,
                role_code=role_code,
                composite=role.composite,
                composites=chain,
                role_type_district=CSS_MARKER_DISTRICT in chain,
                role_type_client=CSS_MARKER_FOREST_CLIENT in chain,
            )
        )

    LOGGER.debug(
        f"Returning {len(options)} selectable role(s) of {len(roles)} CSS role(s) "
        f"for integration {integration_id} ({environment})."
    )
    return options


@router.post(
    "/{integration_id}/{environment}/user-role-assignments",
    response_model=List[CssUserRoleAssignmentResult],
    dependencies=[Depends(jwt_validation.authorize)],
)
def create_css_user_role_assignment(
    integration_id: int, environment: str, request: CssUserRoleAssignmentRequest
):
    """
    Grant a role to a user in CSS, creating a scope-specific role on demand.

    Unscoped: the role is assigned as-is.

    Scoped: one role per scope value is created if it does not already exist,
    named <role>_<SCOPE_TYPE>-<value> (e.g. CHR_FREP_EDITOR_DISTRICT-DCC), and
    those are assigned instead of the base role. That mirrors how FAM generates
    forest client child roles today - the scope has to live in the role name
    because CSS roles carry no attributes and the name is what reaches the token.

    Note the generated role is a plain leaf: it is NOT composed of the base role,
    so a token will contain CHR_FREP_EDITOR_DISTRICT-DCC but not CHR_FREP_EDITOR.
    Consumers authorising on the base role name will need to match on the prefix.

    Roles are created but never removed, so revoking a user leaves the role behind.
    """
    css = CssApiService()
    username = build_css_username(request.user_guid, request.user_type_code)

    if request.scope_values:
        if not request.scope_type:
            raise ValueError("scope_type is required when scope_values are given")
        target_roles = [
            build_scoped_role_name(request.role_name, request.scope_type, value)
            for value in request.scope_values
        ]
    else:
        target_roles = [request.role_name]

    existing = {role.name for role in css.get_roles(integration_id, environment)}

    results: List[CssUserRoleAssignmentResult] = []
    assignable: List[str] = []
    for role_name in target_roles:
        result = CssUserRoleAssignmentResult(role_name=role_name)
        try:
            if role_name not in existing:
                css.create_role(integration_id, environment, role_name)
                result.role_created = True
            assignable.append(role_name)
        except Exception as e:  # keep going, report per role
            result.error_message = str(e)
            LOGGER.warning(f"Could not create CSS role {role_name}: {e}")
        results.append(result)

    if assignable:
        try:
            css.assign_user_roles(integration_id, environment, username, assignable)
            for result in results:
                if result.role_name in assignable:
                    result.assigned = True
        except Exception as e:
            LOGGER.warning(f"Could not assign CSS roles to {username}: {e}")
            for result in results:
                if result.role_name in assignable:
                    result.error_message = str(e)

    LOGGER.debug(f"CSS assignment for {username}: {[r.model_dump() for r in results]}")
    return results


@router.get(
    "/{integration_id}/{environment}/user-role-assignments",
    response_model=List[CssUserRoleRowSchema],
    dependencies=[Depends(jwt_validation.authorize)],
)
def get_css_user_role_assignments(integration_id: int, environment: str):
    """
    Every user/role assignment in an integration, one row per pair.

    CSS has no endpoint listing all users of an integration - only
    GET /roles/{name}/users - so this fans out over every role and merges. Cost is
    one request per role, which grows with every scope-specific role created at
    grant time.

    Scope is recovered by parsing the role name, because that is the only place it
    is recorded. Columns FAM shows but CSS cannot supply - granted-on date, expiry,
    organization - are omitted entirely rather than faked.
    """
    css = CssApiService()
    roles = css.get_roles(integration_id, environment)

    rows: List[CssUserRoleRowSchema] = []
    for role in roles:
        for user in css.get_users_with_role(integration_id, environment, role.name):
            username = user.get("username", "")
            base_role, scope_type, scope_value = parse_scoped_role_name(role.name)
            rows.append(
                CssUserRoleRowSchema(
                    username=username,
                    domain=domain_from_css_username(username),
                    first_name=user.get("firstName"),
                    last_name=user.get("lastName"),
                    email=user.get("email"),
                    role_name=base_role,
                    scope_type=scope_type,
                    scope_value=scope_value,
                )
            )

    LOGGER.debug(
        f"Returning {len(rows)} assignment row(s) from {len(roles)} role(s) "
        f"for integration {integration_id} ({environment})."
    )
    return rows
