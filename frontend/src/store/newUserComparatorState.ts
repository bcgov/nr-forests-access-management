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

/**
 * Compares a list of user role assignments and identifies new users.
 * @param userRoleAssignments An array of user role assignments.
 * @returns A sorted array of user role assignments with an additional property indicating if the user is new.
 */

export const compareUserTable = (
    userRoleAssignments: FamApplicationUserRoleAssignmentGet[] = []
) => {
    // Map over the user role assignments
    const updatedUserRoles = userRoleAssignments.map((userRoleAssignment) => {
        // Check if the user is new
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
        // Extend the user role assignment object with the isNewUser property
        return { ...userRoleAssignment, isNewUser };
    });

    // Sort the updated user roles array
    return updatedUserRoles.sort((first, second) => {
        // Sort first by isNewUser
        if (first.isNewUser === second.isNewUser) {
            // If isNewUser is the same, sort alphabetically by user name
            return first.user.user_name.localeCompare(second.user.user_name);
        }
        // Sort new users first
        return first.isNewUser ? -1 : 1;
    });
};

export const compareAdminTable = (
    userRoleAssignments: FamAppAdminGetResponse[] = []
) => {
    // Map over the user role assignments
    const updatedUserRoles = userRoleAssignments.map((userRoleAssignment) => {
        // Check if the user is new
        const isNewUser = newUsers.value.admin.some((userData) => {
            return (
                userData.user_name.toLocaleUpperCase() ===
                    userRoleAssignment.user.user_name.toLocaleUpperCase() &&
                userData.application_id === userRoleAssignment.application_id
            );
        });
        // Extend the user role assignment object with the isNewUser property
        return { ...userRoleAssignment, isNewUser };
    });

    // Sort the updated user roles array
    return updatedUserRoles.sort((first, second) => {
        // Sort first by isNewUser
        if (first.isNewUser === second.isNewUser) {
            // If isNewUser is the same, sort alphabetically by user name
            return first.user.user_name.localeCompare(second.user.user_name);
        }
        // Sort new users first
        return first.isNewUser ? -1 : 1;
    });
};

export const compareDelTable = (
    userRoleAssignments: FamAccessControlPrivilegeGetResponse[] = []
) => {
    // Map over the user role assignments
    const updatedUserRoles = userRoleAssignments.map((userRoleAssignment) => {
        // Check if the user is new
        const isNewUser = newUsers.value.delegatedAdmin.some((userData) => {
            console.log(userData);
            console.log(userRoleAssignment);
            if (userData.forest_client_numbers) {
                return (
                    userData.user_name.toLocaleUpperCase() ===
                        userRoleAssignment.user.user_name.toLocaleUpperCase() &&
                    userData.role_id === userRoleAssignment.role_id &&
                    userData.forest_client_numbers.some((number) => {
                        return (
                            number ===
                            userRoleAssignment.role.client_number
                                ?.forest_client_number
                        );
                    })
                );
            } else {
                return (
                    userData.user_name.toLocaleUpperCase() ===
                        userRoleAssignment.user.user_name.toLocaleUpperCase() &&
                    userData.role_id === userRoleAssignment.role_id
                );
            }
        });
        // Extend the user role assignment object with the isNewUser property
        return { ...userRoleAssignment, isNewUser };
    });

    // Sort the updated user roles array
    return updatedUserRoles.sort((first, second) => {
        // Sort first by isNewUser
        if (first.isNewUser === second.isNewUser) {
            // If isNewUser is the same, sort alphabetically by user name
            return first.user.user_name.localeCompare(second.user.user_name);
        }
        // Sort new users first
        return first.isNewUser ? -1 : 1;
    });
};
