import { array, mixed, number, object, string } from "yup";
import { UserType, type FamForestClientSchema } from "fam-app-acsctl-api/model";
import type { AddAppPermissionRequestType } from "../../types/RouteTypes";
import type { FamRoleDto } from "fam-admin-mgmt-api/model";

export type AppPermissionFormType = {
    domain: UserType;
    userId: string;
    userGuid: string;
    userEmail: string;
    forestClients: FamForestClientSchema[];
    role: FamRoleDto | null;
    sendUserEmail: boolean;
};

const defaultFormData: AppPermissionFormType = {
    domain: UserType.B,
    userId: "",
    userGuid: "",
    userEmail: "",
    forestClients: [],
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

/**
 * Validation schema for app admin and delegated admin
 */
export const validateAppPermissionForm = (isAbstractRoleSelected: boolean) => {
    return object({
        userId: string()
            .required("User ID is required")
            .min(2, "User ID must be at least 2 characters")
            .nullable(),
        role: mixed<FamRoleDto>().required("Please select a role"),
        forestClients: array()
            .of(
                mixed<FamForestClientSchema>()
                    .required("Each Forest Client must be a valid object")
                    .test(
                        "not-empty-object",
                        "Forest Client cannot be empty",
                        (item) => item && Object.keys(item).length > 0
                    )
            )
            .when("role", {
                is: () => isAbstractRoleSelected,
                then: (schema) =>
                    schema
                        .min(1, "At least one Forest Client is required")
                        .nullable(),
                otherwise: (schema) => schema.nullable(),
            }),
    });
};
