import { Auth } from "aws-amplify";
import type { RouteLocationNormalized, NavigationGuardNext } from "vue-router";

/**
 * Check if the user is authenticated using AWS Amplify
 * @returns {Promise<boolean>}
 */
export async function isAuthenticated(): Promise<boolean> {
    try {
        await Auth.currentAuthenticatedUser();
        return true;
    } catch {
        return false;
    }
}

/**
 * Auth guard to manage navigation based on authentication state.
 * Redirects unauthenticated users to the landing page.
 */
export async function authGuard(
    _to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext
) {
    const auth = await isAuthenticated();
    if (auth) {
        next(); // User is authenticated, proceed to the route
    } else {
        next({ path: "/" }); // Redirect to the landing page if not authenticated
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
    const auth = await isAuthenticated();
    if (auth) {
        next("/manage-permissions"); // Redirect authenticated users to manage-permissions
    } else {
        next(); // Proceed to LandingView for non-authenticated users
    }
}
