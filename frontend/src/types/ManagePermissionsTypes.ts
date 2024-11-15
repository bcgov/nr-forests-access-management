import type { Component, ComputedRef } from "vue";

export type ManagePermissionsTableType =
    | "FAM_APP_ADMIN"
    | "APP_USER"
    | "DELEGATED_ADMIN";

export type ManagePermissionsTabType = {
    key: ManagePermissionsTableType;
    visible: ComputedRef<boolean>;
    icon: Component;
};

export type ManagePermissionsTabHeaderType = {
    [key in ManagePermissionsTableType]: string;
};
