import { AppActlApiService } from '@/services/ApiServiceFactory';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-app-acsctl-api';
import { shallowRef } from 'vue';

export const userRoleAssignments = shallowRef<
    FamApplicationUserRoleAssignmentGet[]
>([]);

// --- Setter

export const setUserRoleAssignments = (
    newValue: FamApplicationUserRoleAssignmentGet[]
) => {
    userRoleAssignments.value = newValue;
};

// --- Fetching (backend)

export const fetchUserRoleAssignments = async (
    applicationId: number | undefined
) => {
    if (!applicationId) return;

    const userRoleAssignments = (
        await AppActlApiService.applicationsApi.getFamApplicationUserRoleAssignment(
            applicationId
        )
    ).data;

    // sorting
    userRoleAssignments.sort((first, second) => {
        // by user_name
        const userNameCompare = first.user.user_name.localeCompare(
            second.user.user_name
        );
        const roleNameCompare = first.role.role_name.localeCompare(
            second.role.role_name
        );
        return userNameCompare != 0 ? userNameCompare : roleNameCompare;
    });
    setUserRoleAssignments(userRoleAssignments);
};
