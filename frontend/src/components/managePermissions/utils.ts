import type { AdminRoleAuthGroup } from "fam-admin-mgmt-api/model";

/**
 * Generates the header title text for the table based on the application name.
 */
export const getTableHeaderTitle = (
    appName: string,
    authGroup: AdminRoleAuthGroup
): string => {
    switch (authGroup) {
        case "FAM_ADMIN":
            return `${appName} users`;
        case "APP_ADMIN":
            return `${appName} users`;
        case "DELEGATED_ADMIN":
            return `${appName} delegated administrators`;
        default:
            return `${appName} users`;
    }
};

/**
 * Generates a description for the table header section based on the application name.
 */
export const getTableHeaderDescription = (
    appName: string,
    authGroup: AdminRoleAuthGroup
): string => {
    switch (authGroup) {
        case "FAM_ADMIN":
            return `
            This table shows all the users in ${appName} and their permissions levels
            `;
        case "APP_ADMIN":
            return `
            This table shows all the users in ${appName} and their permissions levels
            `;
        case "DELEGATED_ADMIN":
            return `
            This table shows all the delegated administrators in ${appName} and the roles they are allowed to manage for their users
            `;
        default:
            return `This table shows all the users in ${appName} and their permissions levels`;
    }
};
