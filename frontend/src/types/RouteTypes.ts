export type AddAppPermissionRequestType =
    | "addUserPermission"
    | "addDelegatedAdmin";

export type AddAppPermissionRouteProps = {
    requestType: AddAppPermissionRequestType;
    applicationId: number;
};
