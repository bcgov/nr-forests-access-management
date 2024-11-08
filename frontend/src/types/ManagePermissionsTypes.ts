import type { Component, ComputedRef, VNode } from "vue";
import type { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";
import type { MessageProps } from "primevue/message";

export type ManagePermissionsTabTypes = {
    key: AdminRoleAuthGroup;
    visible: ComputedRef<boolean>;
    icon: Component;
};

export type ManagePermissionsTabHeaderType = {
    [key in AdminRoleAuthGroup]: string;
};

export type PermissionNotificationType = {
    serverity: MessageProps["severity"];
    message: string | VNode | (() => VNode);
    hasFullMsg: boolean;
    fullMessage?: string | VNode | (() => VNode);
};
