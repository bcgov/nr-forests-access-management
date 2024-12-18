import {
    AdminRoleAuthGroup,
    type AdminUserAccessResponse,
    type FamForestClientBase,
} from "fam-admin-mgmt-api/model";

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

/**
 * Determines if a user is a delegated admin for a specific application but not an app admin.
 *
 * @param {AdminUserAccessResponse} userAccess - The response containing user access information.
 * @param {number} appId - The ID of the application to check.
 * @returns {boolean} True if the user is a delegated admin but not an app admin for the specified application; otherwise, false.
 */
export const isUserDelegatedAdminOnly = (
    appId: number,
    userAccess?: AdminUserAccessResponse
): boolean => {
    const isAppAdmin = isSelectedAppAuthorized(
        AdminRoleAuthGroup.AppAdmin,
        appId,
        userAccess
    );

    const isDelegatedAdmin = isSelectedAppAuthorized(
        AdminRoleAuthGroup.DelegatedAdmin,
        appId,
        userAccess
    );

    return !isAppAdmin && isDelegatedAdmin;
};

/**
 * Retrieves the list of forest clients associated with a specific application
 * for which the user is a delegated admin.
 *
 * @param {number} appId - The ID of the application to retrieve forest clients for.
 * @param {AdminUserAccessResponse} [userAccess] - The response containing user access information.
 * @returns {FamForestClientBase[]} An array of forest clients if the user is a delegated admin
 * for the specified application; returns an empty array if the user does not have delegated admin access
 * or if the userAccess data is invalid.
 *
 */
export const getForestClientsUnderApp = (
    appId: number,
    userAccess?: AdminUserAccessResponse
): FamForestClientBase[] | null => {
    if (
        !userAccess ||
        !isSelectedAppAuthorized(
            AdminRoleAuthGroup.DelegatedAdmin,
            appId,
            userAccess
        )
    ) {
        return [];
    }

    const forestClients: FamForestClientBase[] =
        userAccess.access
            .find(
                (grantDto) =>
                    grantDto.auth_key === AdminRoleAuthGroup.DelegatedAdmin
            )
            ?.grants.find(
                (grantDetailDto) => grantDetailDto.application.id === appId
            )
            ?.roles?.flatMap(
                (roleGrantDto) => roleGrantDto.forest_clients ?? []
            ) || [];

    return forestClients;
};
