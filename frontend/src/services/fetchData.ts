import { AppActlApiService } from '@/services/ApiServiceFactory';
import { setApplicationsUserAdministers } from '@/store/ApplicationState';
import { setUserRoleAssignments } from '@/store/UserAccessRoleState';

// --- Fetching data (from backend)

export const fetchApplications = async () => {
    const applications = (
        await AppActlApiService.applicationsApi.getApplications()
    ).data;
    // State change.
    setApplicationsUserAdministers(applications);
};

export const fetchUserRoleAssignments = async (
    applicationId: number | undefined
) => {
    if (!applicationId) return;

    const userRoleAssignments = (
        await AppActlApiService.applicationsApi.getFamApplicationUserRoleAssignment(
            applicationId
        )
    ).data;

    // Default sorting
    userRoleAssignments.sort((first, second) => {
        // By user_name
        const userNameCompare = first.user.user_name.localeCompare(
            second.user.user_name
        );
        // By role_name
        const roleNameCompare = first.role.role_name.localeCompare(
            second.role.role_name
        );
        return userNameCompare != 0 ? userNameCompare : roleNameCompare;
    });
    // State change.
    setUserRoleAssignments(userRoleAssignments);
};

/**
 * This will call api to delete userRoleXrefId record from backend and fetch again
 * to refresh the state.
 * @param userRoleXrefId id to delete fam_user_role_assignment record.
 * @param applicationId id to fetch and refresh fam_user_role_assignment records with the applicationId.
 */
export const deletAndRefreshUserRoleAssignments = async (
    userRoleXrefId: number,
    applicationId: number
) => {
    await AppActlApiService.userRoleAssignmentApi.deleteUserRoleAssignment(
        userRoleXrefId
    );

    // When deletion is successful, refresh (fetrch) for frontend state.
    fetchUserRoleAssignments(applicationId);
};

export const fetchApplicationRoles = async (
    applicationId: number | undefined
) => {
    if (!applicationId) return;

    const applicationRoles = (
        await AppActlApiService.applicationsApi.getFamApplicationRoles(
            applicationId
        )
    ).data;
    return applicationRoles;
};
