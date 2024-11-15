import type { Component, ComputedRef } from "vue";
import type { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";

export type ManagePermissionsTabTypes = {
    key: AdminRoleAuthGroup;
    visible: ComputedRef<boolean>;
    icon: Component;
};

export type ManagePermissionsTabHeaderType = {
    [key in AdminRoleAuthGroup]: string;
};
