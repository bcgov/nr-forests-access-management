export type SeverityType = "success" | "warn" | "error";

export const Severity = {
    Success: "success" as SeverityType,
    Warning: "warn" as SeverityType,
    Error: "error" as SeverityType,
} as const;

export type ForestClientNotificationType = {
    type: "Duplicate" | "Error" | "NotExist" | "NotActive";
    severity: SeverityType;
    clientNumbers: string[];
};
