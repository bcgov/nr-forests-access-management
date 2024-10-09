<script setup lang="ts">
import { provide, onMounted, onBeforeUnmount, reactive, readonly } from "vue";
import { useRouter } from "vue-router";
import { Auth } from "aws-amplify";
import {
    CognitoUser,
    CognitoAccessToken,
    CognitoIdToken,
    CognitoRefreshToken,
} from "amazon-cognito-identity-js";
import type { CognitoUserSession } from "amazon-cognito-identity-js";

import type {
    IdpTypes,
    AuthContext,
    FamLoginUser,
    AuthState,
} from "@/types/AuthTypes";
import { AUTH_KEY } from "@/constants/InjectionKeys";
import { FIVE_MINUTES, FIFTEEN_MINUTES } from "@/constants/TimeUnits";
import { IdpProvider } from "@/enum/IdpEnum";
import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import { authState } from "@/providers/authState";

const environmentSettings = new EnvironmentSettings();

const REFRESH_INTERVAL = FIVE_MINUTES;
const INACTIVITY_TIMEOUT = FIFTEEN_MINUTES;

let refreshIntervalId: number | null = null;
let inactivityTimeoutId: number | null = null;

const router = useRouter();

/**
 * Resets the inactivity timeout for user activity tracking.
 */
const resetInactivityTimeout = () => {
    if (inactivityTimeoutId) clearTimeout(inactivityTimeoutId);
    inactivityTimeoutId = window.setTimeout(
        stopSilentRefresh,
        INACTIVITY_TIMEOUT
    );
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
    authState.value = reactive<AuthState>({
        isAuthenticated: false,
        famLoginUser: null,
        cognitoUser: null,
        accessToken: null,
        idToken: null,
        refreshToken: null,
    });
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
        idpProvider: decodedIdToken["identities"][0]["providerName"],
        organization: decodedIdToken["custom:idp_business_name"],
    };
};

/**
 * Handles post-login process, updating authentication state and starting silent refresh.
 */
const handlePostLogin = async () => {
    try {
        const cognitoUser: CognitoUser = await Auth.currentAuthenticatedUser();
        const session: CognitoUserSession = await Auth.currentSession();

        const accessToken: CognitoAccessToken = session.getAccessToken();
        const idToken: CognitoIdToken = session.getIdToken();
        const refreshToken: CognitoRefreshToken = session.getRefreshToken();

        const famLoginUser = getFamLoginUser(idToken);

        authState.value = reactive<AuthState>({
            isAuthenticated: true,
            cognitoUser,
            famLoginUser,
            accessToken,
            idToken,
            refreshToken,
        });

        startSilentRefresh(cognitoUser);
        resetInactivityTimeout();

        window.location.replace("/#/manage-permissions");
    } catch (error) {
        console.log("Authentication Error:", error);
        logout();
    }
};

/**
 * Restores the user's session on page reload.
 */
const restoreSession = async () => {
    try {
        const cognitoUser: CognitoUser = await Auth.currentAuthenticatedUser();
        const session: CognitoUserSession = await Auth.currentSession();

        const accessToken: CognitoAccessToken = session.getAccessToken();
        const idToken: CognitoIdToken = session.getIdToken();
        const refreshToken: CognitoRefreshToken = session.getRefreshToken();

        const famLoginUser = getFamLoginUser(idToken);

        authState.value = reactive<AuthState>({
            isAuthenticated: true,
            cognitoUser,
            famLoginUser,
            accessToken,
            idToken,
            refreshToken,
        });

        startSilentRefresh(cognitoUser);
    } catch (error) {
        console.log("Failed to restore session on reload", error);
        logout();
    }
};

/**
 * Starts silent token refresh process for the authenticated user.
 * @param {CognitoUser} cognitoUser The Cognito user to refresh tokens for.
 */
const startSilentRefresh = (cognitoUser: CognitoUser) => {
    if (refreshIntervalId) clearInterval(refreshIntervalId);

    refreshIntervalId = setInterval(async () => {
        try {
            if (authState.value.refreshToken) {
                cognitoUser.refreshSession(
                    authState.value.refreshToken,
                    (err, session) => {
                        if (err) {
                            console.error("Token refresh failed:", err);
                            logout();
                        } else {
                            authState.value = reactive<AuthState>({
                                ...authState.value,
                                accessToken: session.getAccessToken(),
                                idToken: session.getIdToken(),
                            });
                            console.log("Tokens refreshed successfully.");
                        }
                    }
                );
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
    if (inactivityTimeoutId) clearTimeout(inactivityTimeoutId);

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
    <slot />
</template>
