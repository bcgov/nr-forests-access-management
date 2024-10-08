import {
    createRouter,
    createWebHashHistory,
    createWebHistory,
} from "vue-router";
import type { RouteLocationNormalized, NavigationGuardNext } from "vue-router";
import LandingView from "@/views/LandingView.vue";
import ManagePermissionsView from "@/views/ManagePermissionsView.vue";
import ProtectedLayout from "@/layouts/ProtectedLayout.vue";
import { defineComponent } from "vue";
import { Auth } from "aws-amplify"; // Assuming you're using Amplify for authentication

// Lazy-loaded components for protected routes
const UserDetails = () => import("@/views/UserDetails");
const NotFound = () => import("@/components/NotFound.vue");
const GrantAccessView = () => import("@/views/GrantAccessView.vue");
const GrantApplicationAdminView = () =>
    import("@/views/GrantApplicationAdminView.vue");
const GrantDelegatedAdminView = () =>
    import("@/views/GrantDelegatedAdminView.vue");
const MyPermissionsView = () => import("@/views/MyPermissionsView.vue");

// Inline empty component for AuthCallback
const AuthCallbackComponent = defineComponent({
    template: "<div></div>",
});

// Check if the user is authenticated
async function isAuthenticated() {
    try {
        await Auth.currentAuthenticatedUser(); // Check for authenticated user
        return true;
    } catch (error) {
        return false;
    }
}

// Hash-based routes (main app routes)
const hashRoutes = [
    {
        path: "/",
        name: "Landing",
        component: LandingView,
        async beforeEnter(
            _to: RouteLocationNormalized, // Explicitly type 'to'
            _from: RouteLocationNormalized, // Use '_' to indicate that 'from' is intentionally unused
            next: NavigationGuardNext // Type 'next' as NavigationGuardNext
        ) {
            const auth = await isAuthenticated();
            if (auth) {
                next("/dashboard"); // Redirect to dashboard if authenticated
            } else {
                next(); // Proceed to landing if not authenticated
            }
        },
        meta: {
            requiresAuth: false,
        },
    },
    {
        path: "/dashboard",
        name: "Dashboard",
        component: ProtectedLayout,
        async beforeEnter(
            _to: RouteLocationNormalized,
            _from: RouteLocationNormalized,
            next: NavigationGuardNext
        ) {
            const auth = await isAuthenticated();
            if (!auth) {
                next("/"); // Redirect to landing if not authenticated
            } else {
                next(); // Proceed to dashboard if authenticated
            }
        },
        children: [
            {
                path: "",
                component: ManagePermissionsView,
                name: "ManagePermissions",
                meta: { title: "Manage permissions" },
            },
            {
                path: "grant",
                component: GrantAccessView,
                name: "GrantAccess",
                meta: { title: "Grant Access" },
            },
            {
                path: "grant-app-admin",
                component: GrantApplicationAdminView,
                name: "GrantAppAdmin",
                meta: { title: "Grant Application Admin" },
            },
            {
                path: "grant-delegated-admin",
                component: GrantDelegatedAdminView,
                name: "GrantDelegatedAdmin",
                meta: { title: "Grant Delegated Admin" },
            },
            {
                path: "user-details",
                component: UserDetails,
                name: "UserDetails",
                meta: { title: "User Details" },
            },
            {
                path: "my-permissions",
                component: MyPermissionsView,
                name: "MyPermissions",
                meta: { title: "Check my permissions" },
            },
        ],
        meta: {
            requiresAuth: true, // Protect all child routes with authentication
        },
    },
    {
        path: "/:catchAll(.*)", // Catch-all for undefined routes
        component: NotFound,
    },
];

// Route for handling `/authCallback` separately with `historyRouter`
const historyRoutes = [
    {
        path: "/authCallback",
        name: "AuthCallback",
        component: AuthCallbackComponent,
        meta: {
            requiresAuth: false,
        },
    },
];

// Hash router for the main app
const hashRouter = createRouter({
    history: createWebHashHistory(),
    routes: hashRoutes,
});

// History router for the `/authCallback` route
const historyRouter = createRouter({
    history: createWebHistory(),
    routes: historyRoutes,
});

export { hashRouter, historyRouter };
