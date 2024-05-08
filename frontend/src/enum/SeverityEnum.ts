export enum Severity {
    Success = 'success',
    Warning = 'warn',
    Error = 'error',
}

export enum ErrorCode {
    Conflict = 'Conflict',
    SelfGrantProhibited = 'SelfGrantProhibited',
    Default = 'Default',
}

export const ErrorDescription = {
    SelfGrantProhibited: 'Granting admin privilege to self is not allowed.',
    Default: 'An error has occured.',
};

export enum GrantPermissionType {
    Regular = 'GrantUserAccess',
    DelegatedAdmin = 'GrantDelegatedAdmin',
}
