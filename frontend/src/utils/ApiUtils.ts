import type { AxiosError } from "axios";
import {
    AdminRoleAuthGroup,
    type AdminUserAccessResponse,
    type FamApplicationGrantDto,
} from "fam-admin-mgmt-api/model";

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
