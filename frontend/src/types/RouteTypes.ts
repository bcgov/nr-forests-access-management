import type { Component } from "vue";

export type RouteConfigType = {
    path: string;
    component: () => Promise<Component>;
    name: string;
    meta?: Record<string, unknown>;
    children?: Record<string, RouteConfigType>;
};

export type AddAppPermissionRouteProps = {
    requestType: "addUserPermission" | "addDelegatedAdmin";
    applicationId: number;
};
