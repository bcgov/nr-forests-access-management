import type { Component, ComputedRef } from "vue";

export enum ManagePermissionsTableEnum {
    AppAdmin = "APP_ADMIN",
    AppUser = "APP_USER",
    DelegatedAdmin = "DELEGATED_ADMIN",
    ApplicationAdmin = "APPLICATION_ADMIN",
}

export type ManagePermissionsTabType = {
    key: ManagePermissionsTableEnum;
    visible: ComputedRef<boolean>;
    icon: Component;
};

export type ManagePermissionsTabHeaderType = {
    [key in ManagePermissionsTableEnum]: string;
};
