import type { MessageProps } from "primevue/message";
import type { VNode } from "vue";

export type SeverityType = "success" | "warn" | "error";

export const Severity = {
    Success: "success" as SeverityType,
    Warn: "warn" as SeverityType,
    Error: "error" as SeverityType,
} as const;

export type ForestClientNotificationType = {
    type: "Duplicate" | "Error" | "NotExist" | "NotActive" | "Invalid";
    severity: SeverityType;
    clientNumbers: string[];
};

export type PermissionNotificationType = {
    serverity: MessageProps["severity"];
    message: string | VNode | (() => VNode);
    hasFullMsg: boolean;
    fullMessage?: string | VNode | (() => VNode);
};
