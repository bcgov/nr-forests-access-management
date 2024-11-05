export type SeverityType = "success" | "warn" | "error";

export const Severity = {
    Success: "success" as SeverityType,
    Warning: "warn" as SeverityType,
    Error: "error" as SeverityType,
} as const;

export enum ErrorCode {
    Conflict = "Conflict",
    SelfGrantProhibited = "SelfGrantProhibited",
    Default = "Default",
}

export const ErrorDescription = {
    SelfGrantProhibited: "Granting admin privilege to self is not allowed.",
    Default: "An error has occured.",
};

export enum GrantPermissionType {
    Regular = "GrantUserAccess",
    DelegatedAdmin = "GrantDelegatedAdmin",
}
