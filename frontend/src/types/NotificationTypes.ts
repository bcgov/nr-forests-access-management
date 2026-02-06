import type { MessageProps } from "primevue/message";
import type { VNode } from "vue";

export enum Severity {
    Success = "success",
    Warn = "warn",
    Error = "error",
}

export type PermissionNotificationType = {
    severity: MessageProps["severity"];
    message: string | VNode | (() => VNode);
    hasFullMsg: boolean;
    fullMessage?: string | VNode | (() => VNode);
};
