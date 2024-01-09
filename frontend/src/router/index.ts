import { createRouter, createWebHistory } from 'vue-router';

import AuthCallback from '@/components/AuthCallbackHandler.vue';
import NotFound from '@/components/NotFound.vue';
import {
    beforeEachRouteHandler,
    beforeEnterHandlers,
} from '@/router/routeHandlers';
import { routeItems } from '@/router/routeItem';
import GrantAccessView from '@/views/GrantAccessView.vue';
import LandingView from '@/views/LandingView.vue';
import ManagePermissionsView from '@/views/ManagePermissionsView.vue';
import { populateBreadcrumb } from '@/store/BreadcrumbState';
import {
    fetchApplicationAdmin,
    fetchApplicationRoles,
    fetchApplications,
    fetchUserRoleAssignments,
} from '@/services/fetchData';
import { selectedApplication } from '@/store/ApplicationState';

// WARNING: any components referenced below that themselves reference the router cannot be automatically hot-reloaded in local development due to circular dependency
// See vitejs issue https://github.com/vitejs/vite/issues/3033 for discussion.
// Symptoms: you will see the following errors in your browser's Javascript console:
// ReferenceError: Cannot access 'ApplicationSelection' before initialization at index.ts:21:18
// Failed to reload /src/components/ApplicationSelection.vue. This could be due to syntax errors or importing non-existent modules.
// Workaround: reload the page in the browser
// Workarounds:
// 1. Reload the page in the browser if the hot-reload fails.
// 2. (Recommended) Within router below use a wrapper view compoent. The component referenced by the wrapper can be hot-reloaded, while updates to the wrapper view would still trigger this issue.
//    There still seem to be cases where page reload is needed.
// 3. (Not recommended) Within router below, use route-level code-splitting which generates a separately loaded javascript file for this route. Syntax: component: () => import(../components/<component>.vue) syntax.
//    This fixes the issue, but seems to break using shared state (e.g. in ApplicationService).

/**
 * meta:
 * - `requiresAuth`:
 *      Means "authentication (logged in)" is required. For router guard.
 *      If not provided or `false` means it is "public" (for everyone without authentication).
 *
 * - `requiresAppSelected`:
 *      Means user should have selected(or default to) an `application` as a context for business logic.
 *      => global "selectedApplication" state is set.
 */
const routes = [
    {
        path: '/',
        name: routeItems.landing.name,
        meta: {
            requiresAuth: false,
            title: 'Welcome to FAM',
            layout: 'SimpleLayout',
            hasBreadcrumb: false,
        },
        component: LandingView,
    },
    {
        path: routeItems.dashboard.path,
        name: routeItems.dashboard.name,
        meta: {
            requiresAuth: true,
            title: routeItems.dashboard.label,
            layout: 'ProtectedLayout',
            hasBreadcrumb: false,
        },
        component: ManagePermissionsView,
        beforeEnter: async (to: any) => {
            let applicationAdmins;
            let userRoleAssignments;
            // Requires fetching applications the user administers.
            await fetchApplications();
            if (selectedApplication.value?.application_id === 1) {
                applicationAdmins = await fetchApplicationAdmin(
                    selectedApplication.value?.application_id
                );

            } else if (selectedApplication.value?.application_id === 2) {
                userRoleAssignments = await fetchUserRoleAssignments(
                        selectedApplication.value?.application_id
                );
            }

            Object.assign(to.meta, { userRoleAssignments: userRoleAssignments, applicationAdmins: applicationAdmins});
            return true;
        },
        props: (route: any) => {
            return {
                // userRoleAssignments is ready for the `component` as props.
                userRoleAssignments: route.meta.userRoleAssignments,
                applicationAdmins: route.meta.applicationAdmins
            };
        },
    },
    {
        path: routeItems.grantUserPermission.path,
        name: routeItems.grantUserPermission.name,
        meta: {
            requiresAuth: true,
            requiresAppSelected: true,
            title: routeItems.grantUserPermission.label,
            layout: 'ProtectedLayout',
            hasBreadcrumb: true,
        },
        component: GrantAccessView,
        beforeEnter: beforeEnterHandlers[routeItems.grantUserPermission.name],
        props: (route: any) => {
            return {
                // options is ready for the `component` as props.
                applicationRoleOptions: route.meta.applicationRoleOptions,
            };
        },
    },
    {
        path: '/authCallback',
        name: 'Cognito Auth (success) Callback',
        meta: {
            requiresAuth: false,
        },
        component: AuthCallback,
    },
    {
        path: '/:catchAll(.*)',
        meta: {
            requiresAuth: false,
        },
        component: NotFound,
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: routes,
});

router.beforeEach(beforeEachRouteHandler);

export { routes };

export default router;
