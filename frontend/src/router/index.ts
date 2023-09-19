import { createRouter, createWebHistory } from 'vue-router';

import AuthCallback from '@/components/AuthCallbackHandler.vue';
import NotFound from '@/components/NotFound.vue';
import AuthService from '@/services/AuthService';
import GrantAccessView from '@/views/GrantAccessView.vue';
import LandingView from '@/views/LandingView.vue';
import ManagePermissionsView from '@/views/ManagePermissionsView.vue';
import SummaryView from '@/views/SummaryView.vue';

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

const routes = [
    {
        path: '/',
        name: 'landing',
        meta: {
            title: 'Welcome to FAM',
            layout: 'SimpleLayout'
        },
        component: LandingView,
    },
    {
        path: '/dashboard',
        name: 'Manage Permissions',
        meta: {
            title: 'Manage Permissions',
            layout: 'ProtectedLayout'
        },
        component: ManagePermissionsView,
    },
    {
        path: '/grant',
        name: 'grant',
        meta: {
            title: 'Grant Access',
            layout: 'ProtectedLayout'
        },
        component: GrantAccessView,
    },
    {
        path: '/summary',
        name: 'summary',
        meta: {
            title: 'Access request summary',
            layout: 'ProtectedLayout'
        },
        component: SummaryView,
    },
    {
        path: '/authCallback',
        name: 'Cognito Auth (success) Callback',
        component: AuthCallback,
    },
    {
        path: '/:catchAll(.*)',
        component: NotFound,
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: routes,
});

router.beforeEach(async (to, from) => {
    // Refresh token first before navigation.
    if (AuthService.state.value.famLoginUser) {
        // condition needed to prevent infinite redirect
        await AuthService.methods.refreshToken();
    }
});

export { routes };

export default router;
