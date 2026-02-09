import type { AxiosError } from "axios";
import {
    AdminRoleAuthGroup,
    type AdminUserAccessResponse,
    type FamApplicationGrantDto,
} from "fam-admin-mgmt-api/model";
import type { FamUserRoleAssignmentCreateRes } from "fam-app-acsctl-api";

/**
 * Formats an Axios error into a string containing the status and error message.
 *
 * @param {AxiosError} err - The Axios error object.
 * @returns {string} A formatted error string in the format "status: message".
 */
export const formatAxiosError = (err: AxiosError): string => {
    let errMsg = err.message;

    if (err.response) {
        // Use 'any' because we don't have this type exported.
        const detail = (err.response.data as any).detail;

        // Check if detail is an array or an object
        const description = Array.isArray(detail) ? null : detail?.description;

        if (description) {
            errMsg = description ?? err.response.status.toString();
        }
    }
    return errMsg;
};

/**
 * Extracts unique applications from the AdminUserAccessResponse, filtering by `auth_key`.
 *
 * - Only adds applications with `auth_key === "FAM_ADMIN"` if `id === 1`.
 *
 * @param {AdminUserAccessResponse} data - The response containing user access information.
 * @returns {FamApplicationGrantDto[]} An array of unique FamApplicationGrantDto objects.
 */
export const getUniqueApplications = (
    data?: AdminUserAccessResponse
): FamApplicationGrantDto[] => {
    if (!data) {
        return [];
    }

    return Array.from(
        data.access
            .flatMap((authGrant) => {
                // Only include applications under FAM_ADMIN if the application ID is 1
                if (
                    authGrant.auth_key === AdminRoleAuthGroup.FamAdmin &&
                    authGrant.grants.some((grant) => grant.application.id === 1)
                ) {
                    return authGrant.grants
                        .filter((grant) => grant.application.id === 1)
                        .map((grant) => grant.application);
                }
                // Otherwise, include all other applications under other auth_keys
                return authGrant.grants.map((grant) => grant.application);
            })
            .reduce((acc, app) => acc.set(app.id, app), new Map())
            .values()
    );
};

/**
 * Extracts a list of applications that a FAM admin is authorized to grant app admin access for.
 *
 * This function looks for the FAM admin role (`AdminRoleAuthGroup.FamAdmin`) in the provided
 * access response and returns the list of applications associated with the grants assigned
 * to that role.
 *
 * @param {AdminUserAccessResponse} [data] - The access response object containing role-based grants.
 * @returns {FamApplicationGrantDto[]} An array of applications that the FAM admin can grant access to.
 */
export const getFamAdminApplications = (
    data?: AdminUserAccessResponse
): FamApplicationGrantDto[] => {
    if (!data) {
        return [];
    }

    return data.access
        .find((famAccess) => famAccess.auth_key === AdminRoleAuthGroup.FamAdmin)?.grants
        .map((grantDetail) => grantDetail.application) ?? []
};

/**
 * Retrieves a unique application by its ID from the AdminUserAccessResponse.
 *
 * - Filters applications using `getUniqueApplications` to ensure no duplicates.
 * - Searches the resulting unique applications for a matching ID.
 *
 * @param {number} appId - The ID of the application to find.
 * @param {AdminUserAccessResponse} [data] - The response containing user access information.
 * @returns {FamApplicationGrantDto | undefined} The application with the matching ID, or undefined if not found.
 */
export const getApplicationById = (
    appId: number,
    data?: AdminUserAccessResponse
): FamApplicationGrantDto | undefined => {
    if (!data) {
        return;
    }

    const uniqueApps = getUniqueApplications(data);

    return uniqueApps.find((app) => app.id === appId);
};

/**
 * Groups an array of FamUserRoleAssignmentCreateRes items by user ID.
 * @param items An array of FamUserRoleAssignmentCreateRes items to be grouped by user ID.
 * @returns A map where the key is the user ID and the value is an array of
 *          FamUserRoleAssignmentCreateRes items for that user.
 */
export const mapAppUserGrantResponseByUserId = (
    items: Array<FamUserRoleAssignmentCreateRes>
): Map<number, FamUserRoleAssignmentCreateRes[]> => {
    return items.reduce((map, item) => {
        const userId = item.detail!.user_id;
        if (!map.has(userId)) {
            map.set(userId, []);
        }
        map.get(userId)?.push(item);
        return map;
    }, new Map<number, FamUserRoleAssignmentCreateRes[]>());
};