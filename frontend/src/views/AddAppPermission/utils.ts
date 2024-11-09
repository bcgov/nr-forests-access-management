import { array, mixed, object } from "yup";
import {
    UserType,
    type FamForestClientSchema,
    type FamUserRoleAssignmentCreateSchema,
    type IdimProxyBceidInfoSchema,
    type IdimProxyIdirInfoSchema,
} from "fam-app-acsctl-api/model";
import type { AddAppPermissionRequestType } from "../../types/RouteTypes";
import type {
    FamAccessControlPrivilegeCreateRequest,
    FamGrantDetailDto,
    FamRoleDto,
} from "fam-admin-mgmt-api/model";

export const AppAdminSuccessQuerykey = "app-admin-mutation-success";
export const AppAdminErrorQuerykey = "app-admin-mutation-error";
export const DelegatedAdminSuccessQueryKey = "delegated-admin-mutation-success";
export const DelegatedAdminErrorQueryKey = "delegated-admin-mutation-error";

export type AppPermissionFormType = {
    domain: UserType;
    user: IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema | null;
    forestClients: FamForestClientSchema[];
    role: FamRoleDto | null;
    sendUserEmail: boolean;
};

export type AppPermissionQueryErrorType = {
    error: Error;
    formData: AppPermissionFormType;
};

const defaultFormData: AppPermissionFormType = {
    domain: UserType.B,
    user: null,
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
        user: mixed<IdimProxyIdirInfoSchema | IdimProxyBceidInfoSchema>()
            .required("A valid user is required")
            .test("is-user-found", "A valid user ID is required", (value) => {
                return value?.found === true;
            }),
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
                        .min(1, "At least one organization is required")
                        .nullable(),
                otherwise: (schema) => schema.nullable(),
            }),
    });
};

/**
 * Generates a payload for creating a user role assignment or access control privilege request.
 *
 * @param {AppPermissionFormType} formData - The complete form data containing user and role details.
 * @returns {FamUserRoleAssignmentCreateSchema | FamAccessControlPrivilegeCreateRequest} a payload object.
 *
 */
export const generatePayload = (
    formData: AppPermissionFormType
):
    | FamUserRoleAssignmentCreateSchema
    | FamAccessControlPrivilegeCreateRequest => ({
    user_name: formData.user?.userId ?? "",
    user_guid: formData.user?.guid ?? "",
    user_type_code: formData.domain,
    role_id: formData.role?.id ?? -1,
    forest_client_numbers: formData.forestClients.map(
        (fc) => fc.forest_client_number
    ),
    requires_send_user_email: formData.sendUserEmail,
});

/**
 * Retrieves a consolidated application object with unique roles based on the specified application ID.
 *
 * @param {FamGrantDetailDto[]} data - Array of grant details, each containing application and roles information.
 * @param {number} applicationId - The ID of the application to filter and retrieve unique roles for.
 * @returns {{ application: Object, roles: FamRoleDto[] } | null} - An object containing the application details and a list of unique roles, or null if no matching application is found.
 */
export const getApplicationWithUniqueRoles = (
    data: FamGrantDetailDto[],
    applicationId: number
) => {
    const matchedEntries = data.filter(
        (entry) => entry.application.id === applicationId
    );

    if (matchedEntries.length === 0) return null; // Return null if no matches are found

    // Combine unique roles from all matching entries, explicitly filtering out any null or undefined roles
    const uniqueRoles: FamRoleDto[] = [
        ...new Map(
            matchedEntries
                .flatMap((entry) => entry.roles)
                .filter(
                    (role): role is FamRoleDto =>
                        role !== null && role !== undefined
                ) // Narrow type to FamRoleDto
                .map((role) => [role.id, role]) // Use role id as the map key for uniqueness
        ).values(),
    ];

    // Use the first matching entry for the application details
    return {
        application: matchedEntries[0].application,
        roles: uniqueRoles,
    };
};
