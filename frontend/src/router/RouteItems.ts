import type { RouteRecordRaw } from "vue-router";

// Define a constant for ProtectedLayout meta
const protectedLayoutMeta = { layout: "ProtectedLayout" };

export const routeItems: RouteRecordRaw[] = [
    {
        path: "/",
        name: "Landing",
        component: () => import("@/views/LandingView.vue"),
    },
    {
        path: "/manage-permissions",
        name: "ManagePermissions",
        component: () => import("@/views/ManagePermissionsView.vue"),
        meta: protectedLayoutMeta,
        children: [
            {
                path: "grant",
                component: () => import("@/views/GrantAccessView.vue"),
                name: "GrantAccess",
                meta: protectedLayoutMeta,
            },
            {
                path: "grant-app-admin",
                component: () =>
                    import("@/views/GrantApplicationAdminView.vue"),
                name: "GrantAppAdmin",
                meta: protectedLayoutMeta,
            },
            {
                path: "grant-delegated-admin",
                component: () => import("@/views/GrantDelegatedAdminView.vue"),
                name: "GrantDelegatedAdmin",
                meta: protectedLayoutMeta,
            },
            {
                path: "user-details/applications/:applicationId/users/:userId",
                component: () => import("@/views/UserDetails"),
                name: "UserDetails",
                meta: protectedLayoutMeta,
            },
        ],
    },
    {
        path: "/my-permissions",
        name: "MyPermissions",
        component: () => import("@/views/MyPermissionsView.vue"),
        meta: protectedLayoutMeta,
    },
    {
        path: "/:catchAll(.*)",
        component: () => import("@/components/NotFound.vue"),
    },
];
