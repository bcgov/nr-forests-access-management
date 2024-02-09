export enum Severity {
    success = 'success',
    warning = 'warn',
    error = 'error',
}

export enum ErrorCode {
    conflict = 'conflict',
    selfGrantProhibited = 'selfGrantProhibited',
    default = 'default',
}

export enum ErrorDescription{
    selfGrantProhibited = 'Granting admin privilege to self is not allowed.',
    default = 'An error has occured.',
}
