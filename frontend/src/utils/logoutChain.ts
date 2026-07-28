/**
 * Federated logout-chain URL builder.
 *
 * This builds a multi-hop logout chain where each identity layer clears its own
 * session and then redirects to the next, ending back at the app:
 *
 *     app  →  Siteminder logoff.cgi  →  Keycloak end-session  →  Cognito /logout  →  app
 *
 * Cognito fires LAST: that way
 * Keycloak's `post_logout_redirect_uri` is a single, stable, app-agnostic value
 * (the Cognito `/logout` URL) — the only thing that must live on the shared FAM
 * Keycloak client's allow-list. Per-app / per-environment origins are only ever
 * registered as Cognito sign-out URLs, which FAM controls.
 *
 * Correctness hinges on encoding each nested URL EXACTLY ONCE with
 * `encodeURIComponent` as it is embedded in the outer layer's query string. This
 * preserves the structural `?` and `&` of an inner URL through the outer layer's
 * query parse. Without it, `logoff.cgi` peels an inner URL's `?...&...` off as
 * its own query params, silently dropping `post_logout_redirect_uri` at the
 * Siteminder hop — so Keycloak never learns where to go next and the chain breaks.
 */

import { getEnvValue } from "@/utils/EnvUtils";

/**
 * FAM authenticates through two distinct Keycloak (Cognito-as-OIDC-client)
 * clients — one for IDIR, one for BCeID Business. The chain MUST send
 * the client id matching the IdP the user logged in with.
 * `idpProvider` comes from `custom:idp_name` and is `"idir"`or `"bceidbusiness"`.
 */
const keycloakClientIdEnvKeyFor = (
    idpProvider: string | undefined
): string | null => {
    switch (idpProvider?.toLowerCase()) {
        case "idir":
            return "logout_keycloak_client_id_idir";
        case "bceidbusiness":
            return "logout_keycloak_client_id_bceidbusiness";
        default:
            return null;
    }
};

/**
 * Builds the full federated logout-chain URL, nesting innermost → outermost so
 * each layer embeds the one below it.
 *
 * @param appReturnUrl The app origin the browser should land on once the chain
 *   completes (registered as the Cognito `logout_uri`).
 * @param idpProvider The IdP the user logged in with (`"idir"` |
 *   `"bceidbusiness"`) — selects the matching Keycloak client id.
 * @returns The Siteminder logoff URL that drives the whole chain, or `null` if
 *   any required piece of config is missing (caller falls back to Amplify
 *   `signOut()` for a Cognito-only logout).
 */
export const buildFederatedLogoutUrl = (
    appReturnUrl: string,
    idpProvider: string | undefined
): string | null => {
    const keycloakClientIdKey = keycloakClientIdEnvKeyFor(idpProvider);
    const siteminderBase = getEnvValue("logout_siteminder_url");
    const keycloakBase = getEnvValue("logout_keycloak_url");
    const keycloakClientId = keycloakClientIdKey
        ? getEnvValue(keycloakClientIdKey)
        : undefined;
    const cognitoDomain = getEnvValue("fam_cognito_domain");
    const cognitoClientId = getEnvValue("fam_console_web_client_id");
    const appOrigin = appReturnUrl?.trim();

    if (
        !siteminderBase ||
        !keycloakBase ||
        !keycloakClientId ||
        !cognitoDomain ||
        !cognitoClientId ||
        !appOrigin
    ) {
        return null; // → caller falls back to Amplify signOut()
    }

    // Innermost: Cognito clears its own session cookie, then redirects to the app.
    const cognitoLogout =
        `https://${cognitoDomain}.auth.ca-central-1.amazoncognito.com/logout` +
        `?client_id=${encodeURIComponent(cognitoClientId)}` +
        `&logout_uri=${encodeURIComponent(appOrigin)}`;

    // Keycloak clears its session, then returns to the Cognito logout URL. This
    // Cognito URL is the ONLY value registered on the shared FAM Keycloak
    // client's "Valid post logout redirect URIs" — never the app URL.
    const keycloakLogout =
        `${keycloakBase}?client_id=${encodeURIComponent(keycloakClientId)}` +
        `&post_logout_redirect_uri=${encodeURIComponent(cognitoLogout)}`;

    // Outermost: Siteminder logs off the IDIR / BCeID session, then returns to
    // the Keycloak end-session URL. `retnow=1` forces an immediate return with
    // no interstitial.
    return `${siteminderBase}?retnow=1&returl=${encodeURIComponent(keycloakLogout)}`;
};
