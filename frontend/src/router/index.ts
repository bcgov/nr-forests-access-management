import {
    createRouter, createWebHashHistory, createWebHistory
} from 'vue-router';
import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router';

import {
    beforeEachRouteHandler,
    beforeEnterHandlers,
} from '@/router/routeHandlers';
import { routeItems } from '@/router/routeItem';
import { AdminRoleAuthGroup } from 'fam-admin-mgmt-api/model';

// Initial load
import LandingView from '@/views/LandingView.vue';
import ManagePermissionsView from '@/views/ManagePermissionsView.vue';
import AuthCallback from '@/components/AuthCallbackHandler.vue';
import AuthService from '../services/AuthService';

// Lazy load all components
const UserDetails = () => import('@/views/UserDetails');
const NotFound = () => import('@/components/NotFound.vue');
const GrantAccessView = () => import('@/views/GrantAccessView.vue');
const GrantApplicationAdminView = () => import('@/views/GrantApplicationAdminView.vue');
const GrantDelegatedAdminView = () => import('@/views/GrantDelegatedAdminView.vue');
const MyPermissionsView = () => import('@/views/MyPermissionsView.vue');

// WARNING: any components referenced below that themselves reference the router cannot be automatically hot-reloaded in local development due to circular dependency
// See vitejs issue https://github.com/vitejs/vite/issues/3033 for discussion.
// Symptoms: you will see the following errors in your browser's Javascript console:
// ReferenceError: Cannot access 'ApplicationSelection' before initialization at index.ts:21:18
// Failed to reload /src/components/ApplicationSelection.vue. This could be due to syntax errors or importing non-existent modules.
// Workaround: reload the page in the browser
// Workarounds:
// 1. Reload the page in the browser if the hot-reload fails.
// 2. (Recommended) Within router below use a wrapper view component. The component referenced by the wrapper can be hot-reloaded, while updates to the wrapper view would still trigger this issue.
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
 *      Means user should have selected (or default to) an `application` as a context for business logic.
 *      => global "selectedApplication" state is set.
 */


// Routes using createWebHashHistory
const hashRoutes = [
    {
        path: '/',
        name: routeItems.landing.name,
        meta: {
            requiresAuth: false,
            title: 'Welcome to FAM',
            layout: 'SimpleLayout',
            hasBreadcrumb: false,
        },
        beforeEnter: (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
            if (AuthService.isLoggedIn()) {
                next({ name: routeItems.dashboard.name });
            } else {
                next();
            }
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
        path: routeItems.userDetails.path,
        name: routeItems.userDetails.name,
        meta: {
            requiresAuth: true,
            requiresAppSelected: true,
            title: routeItems.userDetails.label,
            layout: 'ProtectedLayout',
            hasBreadcrumb: false,
        },
        component: UserDetails,
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
        path: '/:catchAll(.*)',
        meta: {
            requiresAuth: false,
        },
        component: NotFound,
    },
];

/**
 * Router for `authCallback` using `createWebHistory`.
 *
 * This router is separated to ensure that the `authCallback` URL does not have a `#` prefix,
 * providing a clean URL for authentication callbacks without further configurations.
 */
const historyRouter = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/authCallback',
            name: 'Cognito Auth (success) Callback',
            meta: {
                requiresAuth: false,
            },
            component: AuthCallback,
        },
    ],
});

// Router for all other routes using `createWebHashHistory`
const hashRouter = createRouter({
    history: createWebHashHistory(import.meta.env.BASE_URL),
    routes: hashRoutes,
});

hashRouter.beforeEach(beforeEachRouteHandler);

export { historyRouter, hashRouter, hashRoutes };
