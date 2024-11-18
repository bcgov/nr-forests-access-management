import type { AxiosError } from "axios";
import {
    AdminRoleAuthGroup,
    type AdminUserAccessResponse,
    type FamApplicationDto,
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
            errMsg = `${err.response.status}: ${description}`;
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
 * @returns {FamApplicationDto[]} An array of unique FamApplicationDto objects.
 */
export const getUniqueApplications = (
    data?: AdminUserAccessResponse
): FamApplicationDto[] => {
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
 * Checks if the selected application has the specified authorization key.
 *
 * @param {AdminRoleAuthGroup} authKey - The authorization key to check ("APP_ADMIN", "DELEGATED_ADMIN", etc.).
 * @param {number} selectedAppId - The ID of the selected application to check.
 * @param {AdminUserAccessResponse} data - The response containing user access information.
 * @returns {boolean} True if the selected application ID is under the specified authorization key; otherwise, false.
 */
export const isSelectedAppAuthorized = (
    authKey: AdminRoleAuthGroup,
    selectedAppId?: number,
    data?: AdminUserAccessResponse
): boolean => {
    if (!data || !selectedAppId) {
        return false;
    }

    return data.access.some(
        (authGrant) =>
            authGrant.auth_key === authKey &&
            authGrant.grants.some(
                (grant) => grant.application.id === selectedAppId
            )
    );
};
