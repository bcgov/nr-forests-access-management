/*
 When adding a new route:
 1. Define the route as a constant object using `RouteRecordRaw`.
 2. Use `meta: { layout: "ProtectedLayout" }` if the route requires the ProtectedLayout.
 3. Add the new route constant to the `routeItems` array below.
 4. Each route must have a name defined.
*/
import type { RouteRecordRaw } from "vue-router";
import type { AddAppPermissionRouteProps } from "@/types/RouteTypes";

const protectedLayoutMeta = { layout: "ProtectedLayout" };

export const LandingRoute: RouteRecordRaw = {
    path: "/",
    name: "Landing",
    component: () => import("@/views/LandingView.vue"),
};

export const ManagePermissionsRoute: RouteRecordRaw = {
    path: "/manage-permissions",
    name: "ManagePermissions",
    component: () => import("@/views/ManagePermissionsView"),
    meta: protectedLayoutMeta,
};

export const AddAppPermissionRoute: RouteRecordRaw = {
    path: "/manage-permissions/add-app-permission",
    component: () => import("@/views/AddAppPermission"),
    props: (route): AddAppPermissionRouteProps => ({
        requestType: route.query
            .requestType as AddAppPermissionRouteProps["requestType"],
        applicationId: Number(route.query.applicationId),
    }),
    name: "AddAppPermission",
    meta: protectedLayoutMeta,
};

export const AddFamPermissionRoute: RouteRecordRaw = {
    path: "/manage-permissions/add-fam-permission",
    component: () => import("@/views/AddFamPermission"),
    name: "AddFamPermission",
    meta: protectedLayoutMeta,
};

export const UserDetailsRoute: RouteRecordRaw = {
    path: "/manage-permissions/user-details/applications/:applicationId/users/:userId",
    component: () => import("@/views/UserDetails"),
    name: "UserDetails",
    meta: protectedLayoutMeta,
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
    AddAppPermissionRoute,
    AddFamPermissionRoute,
    UserDetailsRoute,
    MyPermissionsRoute,
    UnkownRoute,
];
