import { createRouter, createWebHistory } from 'vue-router';

import AuthCallback from '@/components/AuthCallbackHandler.vue';
import NotFound from '@/components/NotFound.vue';
import {
    beforeEachRouteHandler,
    beforeEnterHandlers,
} from '@/router/routeHandlers';
import { routeItems } from '@/router/routeItem';
import GrantAccessView from '@/views/GrantAccessView.vue';
import GrantApplicationAdminView from '@/views/GrantApplicationAdminView.vue';
import LandingView from '@/views/LandingView.vue';
import ManagePermissionsView from '@/views/ManagePermissionsView.vue';
import { AdminRoleAuthGroup } from 'fam-admin-mgmt-api/model';
import GrantDelegatedAdminView from '@/views/GrantDelegatedAdminView.vue';
import MyPermissionsView from '@/views/MyPermissionsView.vue';

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
        beforeEnter: beforeEnterHandlers[routeItems.dashboard.name],
        props: (route: any) => {
            return {
                // userRoleAssignments is ready for the `component` as props.
                userRoleAssignments: route.meta.userRoleAssignments,
                applicationAdmins: route.meta.applicationAdmins,
                delegatedAdmins: route.meta.delegatedAdmins,
                newAppAdminId: route.query.newAppAdminId,
                newUserAccessIds: route.query.newUserAccessIds,
                newDelegatedAdminIds: route.query.newDelegatedAdminIds,
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
    },
    {
        path: routeItems.grantAppAdmin.path,
        name: routeItems.grantAppAdmin.name,
        meta: {
            requiresAuth: true,
            requiresAppSelected: true,
            requiredPrivileges: [AdminRoleAuthGroup.FamAdmin],
            title: routeItems.grantAppAdmin.label,
            layout: 'ProtectedLayout',
            hasBreadcrumb: true,
        },
        component: GrantApplicationAdminView,
        beforeEnter: beforeEnterHandlers[routeItems.grantAppAdmin.name],
    },
    {
        path: routeItems.grantDelegatedAdmin.path,
        name: routeItems.grantDelegatedAdmin.name,
        meta: {
            requiresAuth: true,
            requiresAppSelected: true,
            requiredPrivileges: [AdminRoleAuthGroup.AppAdmin],
            title: routeItems.grantDelegatedAdmin.label,
            layout: 'ProtectedLayout',
            hasBreadcrumb: true,
        },
        component: GrantDelegatedAdminView,
        beforeEnter: beforeEnterHandlers[routeItems.grantDelegatedAdmin.name],
    },
    {
        path: routeItems.myPermissions.path,
        name: routeItems.myPermissions.name,
        meta: {
            requiresAuth: true,
            title: routeItems.myPermissions.label,
            layout: 'ProtectedLayout',
            hasBreadcrumb: false,
        },
        component: MyPermissionsView,
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
