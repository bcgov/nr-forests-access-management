import type { Component } from "vue";

export type RouteConfigType = {
    path: string;
    component: () => Promise<Component>;
    name: string;
    meta?: Record<string, unknown>;
    children?: Record<string, RouteConfigType>;
};

export type AddAppPermissionRequestType =
    | "addUserPermission"
    | "addDelegatedAdmin";

export type AddAppPermissionRouteProps = {
    requestType: AddAppPermissionRequestType;
    applicationId: number;
};
