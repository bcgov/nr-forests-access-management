/*
 When adding a new route:
 1. Define the route as a constant object using `RouteRecordRaw`.
 2. Use `meta: { layout: "ProtectedLayout" }` if the route requires the ProtectedLayout.
 3. Add the new route constant to the `routeItems` array below.
*/
import type { RouteRecordRaw } from "vue-router";

const protectedLayoutMeta = { layout: "ProtectedLayout" };

export const LandingRoute: RouteRecordRaw = {
    path: "/",
    name: "Landing",
    component: () => import("@/views/LandingView.vue"),
};

export const GrantAccessRoute: RouteRecordRaw = {
    path: "grant",
    component: () => import("@/views/GrantAccessView.vue"),
    name: "GrantAccess",
    meta: protectedLayoutMeta,
};

export const GrantAppAdminRoute: RouteRecordRaw = {
    path: "grant-app-admin",
    component: () => import("@/views/GrantApplicationAdminView.vue"),
    name: "GrantAppAdmin",
    meta: protectedLayoutMeta,
};

export const GrantDelegatedAdminRoute: RouteRecordRaw = {
    path: "grant-delegated-admin",
    component: () => import("@/views/GrantDelegatedAdminView.vue"),
    name: "GrantDelegatedAdmin",
    meta: protectedLayoutMeta,
};

export const UserDetailsRoute: RouteRecordRaw = {
    path: "user-details/applications/:applicationId/users/:userId",
    component: () => import("@/views/UserDetails"),
    name: "UserDetails",
    meta: protectedLayoutMeta,
};

export const ManagePermissionsRoute: RouteRecordRaw = {
    path: "/manage-permissions",
    name: "ManagePermissions",
    component: () => import("@/views/ManagePermissionsView.vue"),
    meta: protectedLayoutMeta,
    children: [
        GrantAccessRoute,
        GrantAppAdminRoute,
        GrantDelegatedAdminRoute,
        UserDetailsRoute,
    ],
};

export const MyPermissionsRoute: RouteRecordRaw = {
    path: "/my-permissions",
    name: "MyPermissions",
    component: () => import("@/views/MyPermissionsView.vue"),
    meta: protectedLayoutMeta,
};

export const UnkownRoute: RouteRecordRaw = {
    path: "/:catchAll(.*)",
    component: () => import("@/components/NotFound.vue"),
};

export const routeItems: RouteRecordRaw[] = [
    LandingRoute,
    ManagePermissionsRoute,
    MyPermissionsRoute,
    UnkownRoute,
];
