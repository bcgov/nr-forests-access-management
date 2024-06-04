import { ref } from 'vue';
import type {
    FamApplicationUserRoleAssignmentGet,
    FamUserRoleAssignmentCreate,
} from 'fam-app-acsctl-api/model';
import type {
    FamAccessControlPrivilegeCreateRequest,
    FamAccessControlPrivilegeGetResponse,
    FamAppAdminCreateRequest,
    FamAppAdminGetResponse,
} from 'fam-admin-mgmt-api/model';

// Initialize an array to store new users
export const newUsers = ref({
    user: [] as FamUserRoleAssignmentCreate[],
    admin: [] as FamAppAdminCreateRequest[],
    delegatedAdmin: [] as FamAccessControlPrivilegeCreateRequest[],
});

export const clearNewUserTag = () => newUsers.value = {
    user: [] as FamUserRoleAssignmentCreate[],
    admin: [] as FamAppAdminCreateRequest[],
    delegatedAdmin: [] as FamAccessControlPrivilegeCreateRequest[]
}

/**
 * Compares a list of user role assignments and identifies new users.
 * @param userRoleAssignments An array of user role assignments.
 * @returns A sorted array of user role assignments with an additional property indicating if the user is new.
 */
export const compareUserTable = (
    userRoleAssignments: FamApplicationUserRoleAssignmentGet[] = []
) => {
    const updatedUserRoles = userRoleAssignments.map((userRoleAssignment) => {
        // Check if the user is new
        if(newUsers.value.user) {
            const isNewUser = newUsers.value.user.some((userData) => {
                if (!userData.forest_client_number) {
                    return (
                        userData.user_name.toLocaleUpperCase() ===
                            userRoleAssignment.user.user_name.toLocaleUpperCase() &&
                        userData.role_id === userRoleAssignment.role_id
                    );
                } else {
                    return (
                        userData.user_name.toLocaleUpperCase() ===
                            userRoleAssignment.user.user_name.toLocaleUpperCase() &&
                        userData.role_id === userRoleAssignment.role_id &&
                        userData.forest_client_number ===
                            userRoleAssignment.role.forest_client_number
                    );
                }
            });
            return { ...userRoleAssignment, isNewUser };
        } else {
            return { ...userRoleAssignment, isNewUser: false }
        }
    });

    return updatedUserRoles.sort((first, second) => {
        if (first.isNewUser === second.isNewUser) {
            return first.user.user_name.localeCompare(second.user.user_name);
        }
        // Sort new users first
        return first.isNewUser ? -1 : 1;
    });
};

/**
 * Compares a list of user role assignments and identifies new users.
 * @param applicationAdmins An array of app admin role assignments.
 * @returns A sorted array of app admin role assignments with an additional property indicating if the admin is new.
 */
export const compareAdminTable = (
    applicationAdmins: FamAppAdminGetResponse[] = []
) => {
    // Map over the user role assignments
    const updatedUserRoles = applicationAdmins.map((applicationAdmin) => {
        const isNewUser = newUsers.value.admin.some((userData) => {
            return (
                userData.user_name.toLocaleUpperCase() ===
                applicationAdmin.user.user_name.toLocaleUpperCase() &&
                userData.application_id === applicationAdmin.application_id
            );
        });
        return { ...applicationAdmin, isNewUser };
    });

    return updatedUserRoles.sort((first, second) => {
        if (first.isNewUser === second.isNewUser) {
            return first.user.user_name.localeCompare(second.user.user_name);
        }
        // Sort new users first
        return first.isNewUser ? -1 : 1;
    });
};

/**
 * Compares a list of user role assignments and identifies new users.
 * @param delegatedAdmins An array of delegated admin role assignments.
 * @returns A sorted array of app delegated role assignments with an additional property indicating if the delegated admin is new.
 */
export const compareDelegatedAdminTable = (
    delegatedAdmins: FamAccessControlPrivilegeGetResponse[] = []
) => {
    const updatedUserRoles = delegatedAdmins.map((delegatedAdmin) => {
        const isNewUser = newUsers.value.delegatedAdmin.some((userData) => {
            console.log(userData);
            console.log(delegatedAdmin);
            if (userData.forest_client_numbers) {
                return (
                    userData.user_name.toLocaleUpperCase() ===
                    delegatedAdmin.user.user_name.toLocaleUpperCase() &&
                    userData.role_id === delegatedAdmin.role_id &&
                    userData.forest_client_numbers.some((number) => {
                        return (
                            number ===
                            delegatedAdmin.role.client_number
                                ?.forest_client_number
                        );
                    })
                );
            } else {
                return (
                    userData.user_name.toLocaleUpperCase() ===
                    delegatedAdmin.user.user_name.toLocaleUpperCase() &&
                    userData.role_id === delegatedAdmin.role_id
                );
            }
        });
        return { ...delegatedAdmin, isNewUser };
    });

    return updatedUserRoles.sort((first, second) => {
        if (first.isNewUser === second.isNewUser) {
            return first.user.user_name.localeCompare(second.user.user_name);
        }
        // Sort new users first
        return first.isNewUser ? -1 : 1;
    });
};

/**
 * Resets the table formatters by removing the `isNewUser` property from each object in the array.
 * @param tableData An array of objects representing user role assignments, admin role assignments, or delegated admin role assignments.
 * @returns A new array with the `isNewUser` property removed from each object.
 */
export const resetTable = <T extends { isNewUser?: boolean }>(tableData: T[] = []): Omit<T, 'isNewUser'>[] => {
    return tableData.map(({ isNewUser, ...rest }) => rest);
};