import { authState } from "@/providers/authState";
import type { RouteLocationNormalized, NavigationGuardNext } from "vue-router";

/**
 * Waits for the authentication state to be restored.
 * @returns {Promise<void>}
 */
const waitForAuthRestoration = (): Promise<void> => {
    return new Promise((resolve) => {
        const checkAuthRestored = () => {
            if (authState.value.isAuthRestored) {
                resolve();
            } else {
                setTimeout(checkAuthRestored, 100);
            }
        };
        checkAuthRestored();
    });
};

/**
 * Checks if the user is authenticated based on the current authentication state.
 * @returns {boolean} True if the user is authenticated, otherwise false.
 */
const isAuthenticated = (): boolean => {
    return authState.value.isAuthenticated;
};

/**
 * Checks if the user is authenticated using AWS Amplify.
 * Logs the execution time of the check.
 * @returns {Promise<boolean>} True if the user is authenticated, otherwise false.
 */
export async function checkAuthentication(): Promise<boolean> {
    const startTime = performance.now();
    const isAuth = isAuthenticated();
    const endTime = performance.now();
    console.log(
        `isAuthenticated Execution Time: ${endTime - startTime} milliseconds`
    );
    return isAuth;
}

/**
 * Auth guard that manages navigation based on authentication state.
 * Redirects unauthenticated users to the landing page.
 */
export async function authGuard(
    _to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext
) {
    await waitForAuthRestoration();

    if (await checkAuthentication()) {
        next();
    } else {
        next({ path: "/" });
    }
}

/**
 * Redirects authenticated users to `/manage-permissions` if they attempt to access the landing page.
 */
export async function landingGuard(
    _to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext
) {
    await waitForAuthRestoration();

    if (await checkAuthentication()) {
        next("/manage-permissions");
    } else {
        next();
    }
}
