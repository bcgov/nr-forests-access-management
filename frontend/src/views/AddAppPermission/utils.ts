import { UserType } from "fam-app-acsctl-api/model";
import type { AddAppPermissionRequestType } from "../../types/RouteTypes";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";

export type AppPermissionFormType = {
    domain: UserType;
    userId: string;
    userGuid: string;
    userEmail: string;
    forestClientIds: string[];
    role: FamRoleDto | null;
    sendUserEmail: boolean;
};

const defaultFormData: AppPermissionFormType = {
    domain: UserType.B,
    userId: "",
    userGuid: "",
    userEmail: "",
    forestClientIds: [],
    role: null,
    sendUserEmail: false,
};

export const getDefaultFormData = (
    domain: UserType,
    sendUserEmail: boolean
): AppPermissionFormType => {
    const copy = structuredClone(defaultFormData);
    return {
        ...copy,
        domain,
        sendUserEmail,
    };
};

export const getPageTitle = (
    requestType: AddAppPermissionRequestType
): string =>
    requestType === "addUserPermission"
        ? "Add user permission"
        : "Add a delegated admin";

export const getRoleSectionTitle = (requestType: AddAppPermissionRequestType) =>
    requestType === "addUserPermission"
        ? "User roles"
        : "Assign a role to the user";

export const getRoleSectionSubtitle = (
    requestType: AddAppPermissionRequestType
) =>
    requestType === "addUserPermission"
        ? "User roles"
        : "Assign a role the delgated admin can manage";
