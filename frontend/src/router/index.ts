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
import { Auth } from "aws-amplify";

const UserDetails = () => import("@/views/UserDetails");
const NotFound = () => import("@/components/NotFound.vue");
const GrantAccessView = () => import("@/views/GrantAccessView.vue");
const GrantApplicationAdminView = () =>
    import("@/views/GrantApplicationAdminView.vue");
const GrantDelegatedAdminView = () =>
    import("@/views/GrantDelegatedAdminView.vue");
const MyPermissionsView = () => import("@/views/MyPermissionsView.vue");

const AuthCallbackComponent = defineComponent({
    template: "<div></div>",
});

/**
 * Check if the user is authenticated using AWS Amplify
 * @returns {Promise<boolean>}
 */
async function isAuthenticated(): Promise<boolean> {
    try {
        await Auth.currentAuthenticatedUser();
        return true;
    } catch {
        return false;
    }
}

const hashRoutes = [
    {
        path: "/",
        name: "Landing",
        component: LandingView,
        async beforeEnter(
            _to: RouteLocationNormalized,
            _from: RouteLocationNormalized,
            next: NavigationGuardNext
        ) {
            const auth = await isAuthenticated();
            auth ? next("/manage-permissions") : next();
        },
        meta: {
            requiresAuth: false,
        },
    },
    {
        path: "/manage-permissions",
        name: "ManagePermissions",
        component: ProtectedLayout,
        async beforeEnter(
            _to: RouteLocationNormalized,
            _from: RouteLocationNormalized,
            next: NavigationGuardNext
        ) {
            const auth = await isAuthenticated();
            auth ? next() : next("/");
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
        ],
        meta: {
            requiresAuth: true,
        },
    },
    {
        path: "/my-permissions",
        component: ProtectedLayout,
        async beforeEnter(
            _to: RouteLocationNormalized,
            _from: RouteLocationNormalized,
            next: NavigationGuardNext
        ) {
            const auth = await isAuthenticated();
            auth ? next() : next("/");
        },
        children: [
            {
                path: "",
                name: "MyPermissions",
                component: MyPermissionsView,
                meta: { title: "Check my permissions" },
            },
        ],
        meta: {
            requiresAuth: true,
        },
    },
    {
        path: "/:catchAll(.*)",
        component: NotFound,
    },
];

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

const hashRouter = createRouter({
    history: createWebHashHistory(),
    routes: hashRoutes,
});

const historyRouter = createRouter({
    history: createWebHistory(),
    routes: historyRoutes,
});

export { hashRouter, historyRouter };
