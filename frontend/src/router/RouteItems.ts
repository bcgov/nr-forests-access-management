import type { RouteRecordRaw } from "vue-router";
import ProtectedLayout from "@/layouts/ProtectedLayout.vue";

export const routeItems: RouteRecordRaw[] = [
    {
        path: "/",
        name: "Landing",
        component: () => import("@/views/LandingView.vue"),
    },
    {
        path: "/manage-permissions",
        name: "ManagePermissions",
        component: ProtectedLayout,
        children: [
            {
                path: "",
                component: () => import("@/views/ManagePermissionsView.vue"),
                name: "ManagePermissions",
            },
            {
                path: "grant",
                component: () => import("@/views/GrantAccessView.vue"),
                name: "GrantAccess",
            },
            {
                path: "grant-app-admin",
                component: () =>
                    import("@/views/GrantApplicationAdminView.vue"),
                name: "GrantAppAdmin",
            },
            {
                path: "grant-delegated-admin",
                component: () => import("@/views/GrantDelegatedAdminView.vue"),
                name: "GrantDelegatedAdmin",
            },
            {
                path: "user-details/applications/:applicationId/users/:userId",
                component: () => import("@/views/UserDetails"),
                name: "UserDetails",
            },
        ],
    },
    {
        path: "/my-permissions",
        name: "MyPermissions",
        component: ProtectedLayout,
        children: [
            {
                path: "",
                component: () => import("@/views/MyPermissionsView.vue"),
                name: "ManagePermissionsView",
            },
        ],
    },
    {
        path: "/:catchAll(.*)",
        component: () => import("@/components/NotFound.vue"),
    },
];
