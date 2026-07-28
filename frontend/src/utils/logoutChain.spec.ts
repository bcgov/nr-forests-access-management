import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { buildFederatedLogoutUrl } from "@/utils/logoutChain";

const APP_ORIGIN = "http://localhost:5173";
const SITEMINDER = "https://logontest7.gov.bc.ca/clp-cgi/logoff.cgi";
const KEYCLOAK = "https://test.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/logout";
const KC_CLIENT_IDIR = "fsa-cognito-idir-dev-4088";
const KC_CLIENT_BCEID = "fsa-cognito-b-ce-id-business-dev-4090";
const COGNITO_DOMAIN = "lza-dev-fam-user-pool-domain";
const COGNITO_WEB_CLIENT = "7qtdtska897dt6kandveusvd88";

const asEnvEntry = (value: string) => ({ sensitive: false, type: "string", value });

const fullEnv = () => ({
    logout_siteminder_url: asEnvEntry(SITEMINDER),
    logout_keycloak_url: asEnvEntry(KEYCLOAK),
    logout_keycloak_client_id_idir: asEnvEntry(KC_CLIENT_IDIR),
    logout_keycloak_client_id_bceidbusiness: asEnvEntry(KC_CLIENT_BCEID),
    fam_cognito_domain: asEnvEntry(COGNITO_DOMAIN),
    fam_console_web_client_id: asEnvEntry(COGNITO_WEB_CLIENT),
});

const setEnv = (env: Record<string, unknown>) =>
    window.localStorage.setItem("env_data", JSON.stringify(env));

describe("buildFederatedLogoutUrl", () => {
    beforeEach(() => {
        window.localStorage.clear();
    });
    afterEach(() => {
        window.localStorage.clear();
    });

    it("builds the full IDIR chain with the IDIR keycloak client id", () => {
        setEnv(fullEnv());

        const url = buildFederatedLogoutUrl(APP_ORIGIN, "idir");

        expect(url).not.toBeNull();
        // Outermost hop is Siteminder with retnow=1.
        expect(url!.startsWith(`${SITEMINDER}?retnow=1&returl=`)).toBe(true);
        // IDIR client id is used, not BCeID.
        expect(url).toContain(encodeURIComponent(KC_CLIENT_IDIR));
        expect(url).not.toContain(encodeURIComponent(KC_CLIENT_BCEID));
    });

    it("uses the BCeID keycloak client id for a bceidbusiness login", () => {
        setEnv(fullEnv());

        const url = buildFederatedLogoutUrl(APP_ORIGIN, "bceidbusiness");

        expect(url).toContain(encodeURIComponent(KC_CLIENT_BCEID));
        expect(url).not.toContain(encodeURIComponent(KC_CLIENT_IDIR));
    });

    it("is case-insensitive on the idpProvider", () => {
        setEnv(fullEnv());

        expect(buildFederatedLogoutUrl(APP_ORIGIN, "IDIR")).toContain(
            encodeURIComponent(KC_CLIENT_IDIR)
        );
    });

    it("nests each layer with exactly one encodeURIComponent", () => {
        setEnv(fullEnv());

        const url = buildFederatedLogoutUrl(APP_ORIGIN, "idir")!;

        // Peel Siteminder's returl → the Keycloak logout URL, single-decoded.
        const returl = decodeURIComponent(url.split("returl=")[1]);
        expect(returl.startsWith(`${KEYCLOAK}?client_id=`)).toBe(true);
        expect(returl).toContain("post_logout_redirect_uri=");

        // Peel Keycloak's post_logout_redirect_uri → the Cognito logout URL.
        const cognitoLogout = decodeURIComponent(
            returl.split("post_logout_redirect_uri=")[1]
        );
        expect(
            cognitoLogout.startsWith(
                `https://${COGNITO_DOMAIN}.auth.ca-central-1.amazoncognito.com/logout?client_id=`
            )
        ).toBe(true);

        // Innermost logout_uri decodes cleanly back to the app origin.
        const logoutUri = decodeURIComponent(
            cognitoLogout.split("logout_uri=")[1]
        );
        expect(logoutUri).toBe(APP_ORIGIN);
    });

    it("returns null for an unknown idpProvider", () => {
        setEnv(fullEnv());

        expect(buildFederatedLogoutUrl(APP_ORIGIN, "bcsc")).toBeNull();
        expect(buildFederatedLogoutUrl(APP_ORIGIN, undefined)).toBeNull();
    });

    it("returns null when any chain env var is missing", () => {
        const env = fullEnv();
        delete (env as Record<string, unknown>).logout_siteminder_url;
        setEnv(env);

        expect(buildFederatedLogoutUrl(APP_ORIGIN, "idir")).toBeNull();
    });

    it("returns null when the app return url is empty", () => {
        setEnv(fullEnv());

        expect(buildFederatedLogoutUrl("", "idir")).toBeNull();
    });

    it("returns null when env_data is absent entirely", () => {
        expect(buildFederatedLogoutUrl(APP_ORIGIN, "idir")).toBeNull();
    });
});
