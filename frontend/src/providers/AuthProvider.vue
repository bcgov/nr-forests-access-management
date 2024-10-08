<script setup lang="ts">
import { provide, ref, onMounted, onBeforeUnmount, reactive } from "vue";
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

// Constants
const REFRESH_INTERVAL = FIVE_MINUTES; // 5 minutes before token expires
const INACTIVITY_TIMEOUT = FIFTEEN_MINUTES; // 15 minutes of inactivity

let refreshIntervalId: number | null = null; // Use number for browser timers
let inactivityTimeoutId: number | null = null;

// Functions to detect activity
const resetInactivityTimeout = () => {
    if (inactivityTimeoutId) clearTimeout(inactivityTimeoutId);
    inactivityTimeoutId = window.setTimeout(
        stopSilentRefresh,
        INACTIVITY_TIMEOUT
    );
};

const stopSilentRefresh = () => {
    if (refreshIntervalId) clearInterval(refreshIntervalId);
    refreshIntervalId = null;
};

// Login function
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

// Logout function
const logout = async () => {
    await Auth.signOut();
    stopSilentRefresh(); // Stop the silent refresh when logging out
    authState.value = reactive<AuthState>({
        isAuthenticated: false,
        famLoginUser: null,
        cognitoUser: null,
        accessToken: null,
        idToken: null,
        refreshToken: null,
    });
};

// Get user information from the ID token
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

// Handle post-login (OAuth callback handling)
const handlePostLogin = async () => {
    try {
        const cognitoUser: CognitoUser = await Auth.currentAuthenticatedUser();
        const session: CognitoUserSession = await Auth.currentSession();

        const accessToken: CognitoAccessToken = session.getAccessToken();
        const idToken: CognitoIdToken = session.getIdToken();
        const refreshToken: CognitoRefreshToken = session.getRefreshToken();

        const famLoginUser = getFamLoginUser(idToken);

        // Update auth state
        authState.value = reactive<AuthState>({
            isAuthenticated: true,
            cognitoUser,
            famLoginUser,
            accessToken,
            idToken,
            refreshToken,
        });

        // Start silent refresh and inactivity timer
        startSilentRefresh(cognitoUser);
        resetInactivityTimeout(); // Start inactivity timer

        // Navigate to dashboard or appropriate route
        window.location.replace("/");
    } catch (error) {
        console.log("Authentication Error:", error);
        logout();
    }
};

// Handle page reload and session restore
const restoreSession = async () => {
    try {
        const cognitoUser: CognitoUser = await Auth.currentAuthenticatedUser();
        const session: CognitoUserSession = await Auth.currentSession();

        const accessToken: CognitoAccessToken = session.getAccessToken();
        const idToken: CognitoIdToken = session.getIdToken();
        const refreshToken: CognitoRefreshToken = session.getRefreshToken();

        const famLoginUser = getFamLoginUser(idToken);

        // Restore auth state
        authState.value = reactive<AuthState>({
            isAuthenticated: true,
            cognitoUser,
            famLoginUser,
            accessToken,
            idToken,
            refreshToken,
        });

        // Start silent refresh
        startSilentRefresh(cognitoUser);
    } catch (error) {
        console.log("Failed to restore session on reload", error);
        logout(); // Logout if there's any issue with restoring the session
    }
};

// Silent refresh logic
const startSilentRefresh = (cognitoUser: CognitoUser) => {
    if (refreshIntervalId) clearInterval(refreshIntervalId); // Clear any existing interval

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
                            // Update tokens in the state (replace the entire state)
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

// Track user activity for inactivity timeout
onMounted(() => {
    window.addEventListener("mousemove", resetInactivityTimeout);
    window.addEventListener("keydown", resetInactivityTimeout);

    const currentPath = window.location.pathname;
    if (currentPath === "/authCallback") {
        handlePostLogin();
    } else {
        restoreSession(); // Restore session on reload if not on authCallback
    }
});

onBeforeUnmount(() => {
    stopSilentRefresh(); // Clean up refresh interval
    if (inactivityTimeoutId) clearTimeout(inactivityTimeoutId);

    window.removeEventListener("mousemove", resetInactivityTimeout);
    window.removeEventListener("keydown", resetInactivityTimeout);
});

// Provide authentication state and functions
provide<AuthContext>(AUTH_KEY, {
    get authState() {
        return authState.value;
    },
    login,
    logout,
    handlePostLogin,
});
</script>

<template>
    <slot />
</template>
