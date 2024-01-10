import { FamRouteError, RouteErrorName } from '@/errors/FamCustomError';
import { routeItems } from '@/router/routeItem';
import AuthService from '@/services/AuthService';
import {
    fetchApplicationRoles,
    fetchApplications,
    fetchUserRoleAssignments,
} from '@/services/fetchData';
import { asyncWrap } from '@/services/utils';
import {
    isApplicationSelected,
    selectedApplication,
} from '@/store/ApplicationState';
import { populateBreadcrumb } from '@/store/BreadcrumbState';
import { setNavigationPath } from '@/store/NavigationState';
import { setRouteToastError as emitRouteToastError } from '@/store/ToastState';
import type { RouteLocationNormalized } from 'vue-router';

/**
 * This file should contain only the Vue router handler and necessary
 * helpers for router's life-cycle methods (beforeEach, beforeEnter etc...)
 *
 * Vue router does not wrap javascript error nicely.
 * PimeVue Toast (current version) also has limitation which it cannot be used
 * outside of Vue <setup>. This is the case in router.
 * So, here in case of custom error (javascript error), emit the error to a
 * state for it to be handled elsewhere.
 */

// --- beforeEnter Route Handler

const beforeEnterDashboardRoute = async (to: RouteLocationNormalized) => {
    // Requires fetching applications the user administers.
    await asyncWrap(fetchApplications());
    const userRolesFetchResult = await asyncWrap(
        fetchUserRoleAssignments(selectedApplication.value?.application_id)
    );
    Object.assign(to.meta, { userRoleAssignments: userRolesFetchResult.data });
    return true;
};

const beforeEnterGrantUserPermissionRoute = async (
    to: RouteLocationNormalized
) => {
    populateBreadcrumb([routeItems.dashboard, routeItems.grantUserPermission]);

    const appRolesFetchResult = await asyncWrap(
        fetchApplicationRoles(selectedApplication.value!.application_id)
    );
    if (appRolesFetchResult.error) {
        emitRouteToastError(appRolesFetchResult.error);
        return { path: routeItems.dashboard.path };
    }

    // Passing fetched data to router.meta (so it is available for assigning to 'props' later)
    Object.assign(to.meta, {
        applicationRoleOptions: appRolesFetchResult.data,
    });
    return true;
};

export const beforeEnterHandlers = {
    [routeItems.dashboard.name]: beforeEnterDashboardRoute,
    [routeItems.grantUserPermission.name]: beforeEnterGrantUserPermissionRoute,
};

// --- beforeEach Route Handler

// Responsible for route guards and necessary operations before each route.
export const beforeEachRouteHandler = async (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized
) => {
    // Authentication guard. Always check first.
    if (to.meta.requiresAuth && !AuthService.getters.isLoggedIn()) {
        // Only to compose this custom error, but not to throw.
        // Due to throwing error from router cannot be caught by Primevue toast.
        // The RouteError will be emitted to a state.
        const routeError = new FamRouteError(
            RouteErrorName.NOT_AUTHENTICATED_ERROR,
            "You're not logged in. Please login.",
            { to, from }
        );
        emitRouteToastError(routeError);
        // Back to Landing after emit error.
        setNavigationPath(to.path);
        return { path: routeItems.landing.path };
    }

    if (AuthService.getters.isLoggedIn() && to.path != routeItems.accessRequest.path && !AuthService.getters.userHasRoles()) {
        const routeError = new FamRouteError(
            RouteErrorName.NO_ROLES_ERROR,
            "You do not have any FAM roles. Please request access.",
            { to, from }
        );
        emitRouteToastError(routeError);
        return { path: routeItems.accessRequest.path };
    }

    // Application selected guard.
    if (to.meta.requiresAppSelected && !isApplicationSelected.value) {
        const routeError = new FamRouteError(
            RouteErrorName.NO_APPLICATION_SELECTED_ERROR,
            'No application is Selected',
            { to, from }
        );
        emitRouteToastError(routeError);
        // Back to dashboard after emit error.
        return { path: routeItems.dashboard.path };
    }

    // Refresh token before navigation.
    if (AuthService.state.value.famLoginUser) {
        // condition needed to prevent infinite redirect
        await AuthService.methods.refreshToken();
    }
};
