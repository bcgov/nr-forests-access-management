import {
    AdminRoleAuthGroup,
    type AdminUserAccessResponse,
    type FamAuthGrantDto,
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
