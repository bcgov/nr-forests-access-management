import { FamRouteError, RouteErrorName } from "@/errors/FamCustomError";
import { routeItems } from '@/router/routeItem';
import AuthService from "@/services/AuthService";
import { isApplicationSelected } from "@/store/ApplicationState";
import { setRouteToastError as emitRouteToastError } from '@/store/ToastState';
import type { RouteLocationNormalized } from "vue-router";

// Route `beforeEach` handler.
// Responsible for route guards and necessary operations before each route.
export const beforeEachRouteHandler = async (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized) => {

    // Authentication guard. Always check first.
    if (to.meta.requiresAuth && !AuthService.getters.isLoggedIn()) {
        // Only to compose this custom error, but not to throw.
        // Due to throwing error from router cannot be caught by Primevue toast.
        // The RouteError will be emitted to a state.
        const routeError = new FamRouteError(
            RouteErrorName.NOT_AUTHENTICATED_ERROR,
            "You're not login",
            {to, from}
        )
        emitRouteToastError(routeError);
        // Back to Landing after emit error.
        return {path: routeItems.landing.path}
    }

    // Application selected guard.
    if (to.meta.requiresAppSelected && !isApplicationSelected.value) {
        const routeError = new FamRouteError(
            RouteErrorName.NO_APPLICATION_SELECTED_ERROR,
            'No application is Selected',
            {to, from}
        )
        emitRouteToastError(routeError);
        // Back to dashboard after emit error.
        return {path: routeItems.dashboard.path};
    }

    // Refresh token before navigation.
    if (AuthService.state.value.famLoginUser) {
        // condition needed to prevent infinite redirect
        await AuthService.methods.refreshToken();
    }
}
