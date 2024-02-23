import { FamRouteError, RouteErrorName } from '@/errors/FamCustomError';
import { routeItems } from '@/router/routeItem';
import AuthService from '@/services/AuthService';
import {
    fetchApplicationRoles,
    fetchApplicationAdmins,
    fetchUserRoleAssignments,
    fetchDelegatedAdmins,
} from '@/services/fetchData';
import { asyncWrap } from '@/services/utils';
import {
    isApplicationSelected,
    selectedApplication,
    selectedApplicationId,
} from '@/store/ApplicationState';
import { populateBreadcrumb } from '@/store/BreadcrumbState';
import { FAM_APPLICATION_ID } from '@/store/Constants';
import LoginUserState from '@/store/FamLoginUserState';
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

const ACCESS_RESTRICTED_ERROR = new FamRouteError(
    RouteErrorName.ACCESS_RESTRICTED,
    'Access restricted'
);

// --- beforeEnter Route Handler

const beforeEnterDashboardRoute = async (to: RouteLocationNormalized) => {
    let applicationAdmins;
    let userRolesFetchResult;
    let delegatedAdmins;

    delegatedAdmins = await asyncWrap(fetchDelegatedAdmins(selectedApplicationId.value))
    // Requires fetching applications the user administers.
    delegatedAdmins = await asyncWrap(
        fetchDelegatedAdmins(selectedApplicationId.value)
    );
    if (selectedApplicationId.value === FAM_APPLICATION_ID) {
        applicationAdmins = await asyncWrap(fetchApplicationAdmins());
    } else {
        userRolesFetchResult = await asyncWrap(
            fetchUserRoleAssignments(selectedApplicationId.value)
        );
    }
    Object.assign(to.meta, {
        userRoleAssignments: userRolesFetchResult?.data,
        applicationAdmins: applicationAdmins?.data,
        delegatedAdmins: delegatedAdmins?.data,
    });
    return true;
};

const beforeEnterGrantUserPermissionRoute = async (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized
) => {
    if (selectedApplicationId.value === FAM_APPLICATION_ID) {
        emitRouteToastError(ACCESS_RESTRICTED_ERROR);
        return { path: routeItems.dashboard.path };
    }

    const appRolesFetchResult = await asyncWrap(
        fetchApplicationRoles(selectedApplication.value!.id)
    );
    if (appRolesFetchResult.error) {
        emitRouteToastError(appRolesFetchResult.error);
        return { path: routeItems.dashboard.path };
    }

    populateBreadcrumb([routeItems.dashboard, routeItems.grantUserPermission]);
    // Passing fetched data to router.meta (so it is available for assigning to 'props' later)
    Object.assign(to.meta, {
        applicationRoleOptions: appRolesFetchResult.data,
    });
    return true;
};

const beforeEnterGrantApplicationAdminRoute = async (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized
) => {
    if (selectedApplicationId.value !== FAM_APPLICATION_ID) {
        emitRouteToastError(ACCESS_RESTRICTED_ERROR);
        return { path: routeItems.dashboard.path };
    }
    populateBreadcrumb([routeItems.dashboard, routeItems.grantAppAdmin]);
    return true;
};

export const beforeEnterHandlers = {
    [routeItems.dashboard.name]: beforeEnterDashboardRoute,
    [routeItems.grantUserPermission.name]: beforeEnterGrantUserPermissionRoute,
    [routeItems.grantAppAdmin.name]: beforeEnterGrantApplicationAdminRoute,
};

// --- beforeEach Route Handler

// Responsible for route guards and necessary operations before each route.
export const beforeEachRouteHandler = async (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized
) => {
    // Authentication guard. Always check first.
    if (to.meta.requiresAuth && !AuthService.isLoggedIn()) {
        // Only to compose this custom error, but not to throw.
        // Due to throwing error from router cannot be caught by Primevue toast.
        // The RouteError will be emitted to a state.
        const routeError = new FamRouteError(
            RouteErrorName.NOT_AUTHENTICATED_ERROR,
            "You're not login",
            { to, from }
        );
        emitRouteToastError(routeError);
        // Back to Landing after emit error.
        return { path: routeItems.landing.path };
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

    // Access privilege guard. This logic might need to be adjusted soon.
    if (to.meta.requiredPrivileges) {
        for (let role of (to.meta.requiredPrivileges as Array<string>)) {
            if (!LoginUserState.hasAccessRole(role)) {
                emitRouteToastError(ACCESS_RESTRICTED_ERROR);
                return { path: routeItems.dashboard.path };
            }
        }
    }

    // Refresh token before navigation.
    if (LoginUserState.state.value.famLoginUser) {
        // condition needed to prevent infinite redirect
        await AuthService.refreshToken();
    }
};
