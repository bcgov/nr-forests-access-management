<script setup lang="ts">
import { ref, provide, onMounted, onBeforeUnmount, readonly } from "vue";
import axios from "axios";
import {
    signInWithRedirect,
    signOut,
    getCurrentUser,
    fetchAuthSession,
    decodeJWT,
} from "aws-amplify/auth";
import type { AuthSession } from "aws-amplify/auth";
import type { IdpTypes, AuthContext, FamLoginUser } from "@/types/AuthTypes";
import { AUTH_KEY } from "@/constants/InjectionKeys";
import { ONE_SECOND, THREE_MINUTES, HALF_HOUR } from "@/constants/TimeUnits";
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

        signInWithRedirect({
            provider: {
                custom: customProvider,
            },
        });
    } catch (error) {
        console.error("Login failed:", error);
    }
};

/**
 * Logs the user out and resets authentication state.
 */
const logout = async () => {
    stopSilentRefresh();

    delete axios.defaults.headers.common["Authorization"];

    authState.value = {
        isAuthenticated: false,
        famLoginUser: null,
        isAuthRestored: true,
    };

    await signOut();
};

/**
 * Extracts user information from the provided ID token.
 * @param {string} idToken The ID token from which to extract user info.
 * @returns {FamLoginUser} The extracted user information.
 */
const getFamLoginUser = (idToken: string): FamLoginUser => {
    const payload: Record<string, any> = decodeJWT(idToken).payload;
    return {
        username: payload["custom:idp_username"],
        displayName: payload["custom:idp_display_name"],
        email: payload["email"],
        idpProvider: payload["custom:idp_name"]?.toLowerCase(),
        organization: payload["custom:idp_business_name"],
    };
};

/**
 * Handles post-login process, updating authentication state and starting silent refresh.
 */
const handlePostLogin = async () => {
    try {
        isLoading.value = true;
        await loadUser();
        startSilentRefresh();
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

/**
 * Restores the user's session on page reload if the user is already authenticated.
 */
const restoreSession = async () => {
    try {
        isLoading.value = true;
        await loadUser();
        startSilentRefresh();
        resetInactivityTimeout();
    } catch (error) {
        console.warn(error);
        authState.value = {
            isAuthenticated: false,
            famLoginUser: null,
            isAuthRestored: true,
        };
    } finally {
        isLoading.value = false;
    }
};

const loadUser = async (): Promise<any> => {
    // forceRefresh to retrieve the latest user attributes after they are changed
    // bypass the local cache without needing the user to sign out and sign back in, similar as bypassCache in v5
    const session: AuthSession = await fetchAuthSession({ forceRefresh: true });

    const accessToken = session.tokens?.accessToken;
    const idToken = session.tokens?.idToken;

    if (!accessToken || !idToken) {
        throw new Error("The user is not authenticated");
    }

    const famLoginUser = getFamLoginUser(idToken.toString());

    authState.value = {
        isAuthenticated: true,
        famLoginUser,
        isAuthRestored: true,
    };

    setAxiosAuthorizationHeader(accessToken.toString());
};

/**
 * Prevents concurrent token refresh attempts, reducing potential race conditions.
 */
let isRefreshing = false;

/**
 * Starts silent token refresh process for the authenticated user.
 */
const startSilentRefresh = () => {
    if (refreshIntervalId) clearInterval(refreshIntervalId);

    refreshIntervalId = setInterval(async () => {
        try {
            if (!isRefreshing) {
                isRefreshing = true;
                loadUser();
            }
        } catch (error) {
            console.error("Silent refresh failed:", error);
            logout();
        } finally {
            isRefreshing = false;
        }
    }, REFRESH_INTERVAL) as unknown as number;
};

/**
 * Creates a debounced version of the provided function, ensuring it is not
 * called more frequently than the specified delay.
 *
 * @template T - The type of the function to debounce.
 * @param {T} func - The function to debounce.
 * @param {number} delay - The delay in milliseconds to wait before invoking the function.
 * @returns {T} A debounced version of the input function.
 *
 * @example
 * const debouncedLog = debounce(() => console.log('Debounced!'), ONE_SECOND);
 * window.addEventListener('resize', debouncedLog);
 *
 * @description
 * This function is useful in scenarios where an operation, such as an API call
 * or DOM manipulation, should not be triggered excessively. It ensures that
 * the input function is executed only after the specified delay has elapsed
 * since the last invocation.
 *
 * In this context, it prevents `resetInactivityTimeout` from being triggered
 * repeatedly during rapid user interactions, such as mouse movements or key presses.
 */
const debounce = <T extends (...args: any[]) => void>(
    func: T,
    delay: number
): T => {
    let timer: ReturnType<typeof setTimeout> | null = null;

    return ((...args: Parameters<T>) => {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => func(...args), delay);
    }) as T;
};

/**
 * A debounced function to reset the inactivity timeout.
 *
 * @description
 * This function resets the inactivity timeout whenever user activity (e.g., mouse movement,
 * keypress) is detected. It ensures the user remains logged in as long as they are active
 * by postponing the logout triggered by inactivity. If no activity is detected within the
 * defined `INACTIVITY_TIMEOUT`, the user is logged out for security reasons.
 *
 * The debounce mechanism minimizes the number of calls to the underlying `resetInactivityTimeout`
 * function, even during rapid, frequent interactions (e.g., continuous mouse movements).
 * This reduces redundant operations and improves performance.
 *
 * @example
 * // Add event listeners for user activity
 * window.addEventListener('mousemove', debouncedResetInactivityTimeout);
 * window.addEventListener('keydown', debouncedResetInactivityTimeout);
 *
 * @see {@link debounce} for how the debounce mechanism works.
 */
const debouncedResetInactivityTimeout = debounce(
    resetInactivityTimeout,
    ONE_SECOND
);

/**
 * Lifecycle hook that runs when the component is mounted.
 * - Adds event listeners for user activity (mousemove and keydown) to reset inactivity timeout.
 * - Checks the current path. If the user is on the `/authCallback` path, it handles the login process.
 * - If not on the `/authCallback` path, it attempts to restore the user's session.
 */
onMounted(() => {
    window.addEventListener("mousemove", debouncedResetInactivityTimeout);
    window.addEventListener("keydown", debouncedResetInactivityTimeout);
    window.addEventListener("click", debouncedResetInactivityTimeout);

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

    window.removeEventListener("mousemove", debouncedResetInactivityTimeout);
    window.removeEventListener("keydown", debouncedResetInactivityTimeout);
    window.removeEventListener("click", debouncedResetInactivityTimeout);
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
