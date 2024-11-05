<script setup lang="ts">
import { ref, provide, onMounted, onBeforeUnmount, readonly } from "vue";
import axios from "axios";
import { Auth } from "aws-amplify";
import type {
    CognitoUser,
    CognitoAccessToken,
    CognitoIdToken,
    CognitoRefreshToken,
} from "amazon-cognito-identity-js";
import type { CognitoUserSession } from "amazon-cognito-identity-js";

import type { IdpTypes, AuthContext, FamLoginUser } from "@/types/AuthTypes";
import { AUTH_KEY } from "@/constants/InjectionKeys";
import { THREE_MINUTES, HALF_HOUR } from "@/constants/TimeUnits";
import { IdpProvider } from "@/enum/IdpEnum";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import { authState } from "@/providers/authState";
import { useRouter } from "vue-router";
import Spinner from "@/components/UI/Spinner.vue";

const environmentSettings = new EnvironmentSettings();
const REFRESH_INTERVAL = THREE_MINUTES;
const INACTIVITY_TIMEOUT = HALF_HOUR;

let refreshIntervalId: number | null = null;
let inactivityTimeoutId: number | null = null;
const isLoading = ref(false); // Loading state for animation
const router = useRouter();

const setAxiosAuthorizationHeader = (token: string) => {
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
};

/**
 * Resets the inactivity timeout and sets a new timeout to log the user out after a period of inactivity.
 * If the user is inactive (no mouse or keyboard input) for the defined `INACTIVITY_TIMEOUT`,
 * and is still authenticated, they will be logged out and the silent refresh will stop.
 */
const resetInactivityTimeout = () => {
    if (inactivityTimeoutId) clearTimeout(inactivityTimeoutId);

    // Set a timeout that logs the user out after inactivity
    inactivityTimeoutId = window.setTimeout(() => {
        if (authState.value.isAuthenticated) {
            console.log("User inactive, logging out.");
            logout();
        }
    }, INACTIVITY_TIMEOUT);
};

/**
 * Stops the silent token refresh process.
 */
const stopSilentRefresh = () => {
    if (refreshIntervalId) clearInterval(refreshIntervalId);
    refreshIntervalId = null;
};

/**
 * Logs in the user using the specified identity provider.
 * @param {IdpTypes} idP The identity provider type (IDIR, BCEIDBUSINESS).
 */
const login = async (idP: IdpTypes) => {
    try {
        const customProvider =
            idP === IdpProvider.IDIR
                ? environmentSettings.getIdentityProviderIdir()
                : environmentSettings.getIdentityProviderBceid();
        await Auth.federatedSignIn({ customProvider });
    } catch (error) {
        console.error("Login failed:", error);
    }
};

/**
 * Logs the user out and resets authentication state.
 */
const logout = async () => {
    await Auth.signOut();
    stopSilentRefresh();

    delete axios.defaults.headers.common["Authorization"];

    authState.value = {
        isAuthenticated: false,
        famLoginUser: null,
        cognitoUser: null,
        accessToken: null,
        idToken: null,
        refreshToken: null,
        isAuthRestored: true,
    };
};

/**
 * Extracts user information from the provided ID token.
 * @param {CognitoIdToken} idToken The ID token from which to extract user info.
 * @returns {FamLoginUser} The extracted user information.
 */
const getFamLoginUser = (idToken: CognitoIdToken): FamLoginUser => {
    const decodedIdToken = idToken.decodePayload();
    return {
        username: decodedIdToken["custom:idp_username"],
        displayName: decodedIdToken["custom:idp_display_name"],
        email: decodedIdToken["email"],
        idpProvider: decodedIdToken["custom:idp_name"]?.toLowerCase(),
        organization: decodedIdToken["custom:idp_business_name"],
    };
};

/**
 * Handles post-login process, updating authentication state and starting silent refresh.
 */
const handlePostLogin = async () => {
    try {
        isLoading.value = true;
        const cognitoUser: CognitoUser = await Auth.currentAuthenticatedUser();
        const session: CognitoUserSession = await Auth.currentSession();

        const accessToken: CognitoAccessToken = session.getAccessToken();
        const idToken: CognitoIdToken = session.getIdToken();
        const refreshToken: CognitoRefreshToken = session.getRefreshToken();

        const famLoginUser = getFamLoginUser(idToken);

        authState.value = {
            isAuthenticated: true,
            cognitoUser,
            famLoginUser,
            accessToken,
            idToken,
            refreshToken,
            isAuthRestored: true,
        };

        setAxiosAuthorizationHeader(accessToken.getJwtToken());

        startSilentRefresh(cognitoUser);
        resetInactivityTimeout();

        /*
         * Update the browser's URL to remove the 'authCallback' part,
         * ensuring a cleaner URL structure without disrupting the Vue Router's state.
         * This prevents the 'authCallback' fragment from appearing in the URL,
         * allowing for a seamless transition to the desired route, '/manage-permissions'.
         *
         * Additionally, this approach results in one fewer comparison check in the auth guard
         * compared to using window.location.replace, optimizing the authentication flow
         * and improving overall performance.
         */
        const newUrl = window.location.href.replace(/authCallback/, "");
        history.replaceState(null, "", newUrl);

        router.push("/manage-permissions");
    } catch (error) {
        console.log("Authentication Error:", error);
        logout();
    } finally {
        isLoading.value = false;
    }
};

const refreshUserSession = (
    cognitoUser: CognitoUser,
    refreshToekn: CognitoRefreshToken
) => {
    cognitoUser.refreshSession(
        refreshToekn,
        (err, session: CognitoUserSession) => {
            if (err) {
                console.error("Token refresh failed:", err);
                logout();
            } else {
                authState.value = {
                    ...authState.value,
                    accessToken: session.getAccessToken(),
                    idToken: session.getIdToken(),
                };
                setAxiosAuthorizationHeader(
                    session.getAccessToken().getJwtToken()
                );
                console.log("Tokens refreshed successfully.");
            }
        }
    );
};

/**
 * Restores the user's session on page reload if the user is already authenticated.
 */
const restoreSession = async () => {
    try {
        isLoading.value = true;
        const cognitoUser: CognitoUser = await Auth.currentAuthenticatedUser();
        const session: CognitoUserSession = await Auth.currentSession();

        const accessToken: CognitoAccessToken = session.getAccessToken();
        const idToken: CognitoIdToken = session.getIdToken();
        const refreshToken: CognitoRefreshToken = session.getRefreshToken();

        const famLoginUser = getFamLoginUser(idToken);

        authState.value = {
            isAuthenticated: true,
            cognitoUser,
            famLoginUser,
            accessToken,
            idToken,
            refreshToken,
            isAuthRestored: true,
        };

        setAxiosAuthorizationHeader(accessToken.getJwtToken());
        refreshUserSession(cognitoUser, refreshToken);
        startSilentRefresh(cognitoUser);
        resetInactivityTimeout();
    } catch (error) {
        console.warn(error);
        authState.value = {
            isAuthenticated: false,
            famLoginUser: null,
            cognitoUser: null,
            accessToken: null,
            idToken: null,
            refreshToken: null,
            isAuthRestored: true,
        };
    } finally {
        isLoading.value = false;
    }
};

/**
 * Starts silent token refresh process for the authenticated user.
 */
const startSilentRefresh = (cognitoUser: CognitoUser) => {
    if (refreshIntervalId) clearInterval(refreshIntervalId);

    refreshIntervalId = setInterval(async () => {
        try {
            if (authState.value.refreshToken) {
                refreshUserSession(cognitoUser, authState.value.refreshToken);
            }
        } catch (error) {
            console.error("Silent refresh failed:", error);
            logout();
        }
    }, REFRESH_INTERVAL) as unknown as number;
};

/**
 * Lifecycle hook that runs when the component is mounted.
 * - Adds event listeners for user activity (mousemove and keydown) to reset inactivity timeout.
 * - Checks the current path. If the user is on the `/authCallback` path, it handles the login process.
 * - If not on the `/authCallback` path, it attempts to restore the user's session.
 */
onMounted(() => {
    window.addEventListener("mousemove", resetInactivityTimeout);
    window.addEventListener("keydown", resetInactivityTimeout);

    const currentPath = window.location.pathname;
    if (currentPath === "/authCallback") {
        handlePostLogin();
    } else {
        restoreSession();
    }
});

/**
 * Lifecycle hook that runs when the component is about to be unmounted.
 * - Stops the silent token refresh process.
 * - Clears the inactivity timeout if it's set.
 * - Removes event listeners for user activity (mousemove and keydown) to prevent memory leaks.
 */
onBeforeUnmount(() => {
    stopSilentRefresh();
    if (inactivityTimeoutId) {
        clearTimeout(inactivityTimeoutId);
    }

    window.removeEventListener("mousemove", resetInactivityTimeout);
    window.removeEventListener("keydown", resetInactivityTimeout);
});

/**
 * Provides authentication state and functions for use in components.
 */
provide<AuthContext>(AUTH_KEY, {
    get authState() {
        return readonly(authState.value);
    },
    login,
    logout,
    handlePostLogin,
});
</script>

<template>
    <div v-if="isLoading" class="auth-callback-container">
        <Spinner loading-text="Page loading" />
    </div>
    <slot v-else />
</template>

<style lang="scss" scoped>
.auth-callback-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100vw;
}
</style>
