import { AppActlApiService, AdminMgmtApiService } from '@/services/ApiServiceFactory';
import { setApplicationsUserAdministers } from '@/store/ApplicationState';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-app-acsctl-api';
import type { FamAppAdminGet } from 'fam-admin-mgmt-api/model';

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
): Promise<FamApplicationUserRoleAssignmentGet[]> => {
    if (!applicationId) return [];

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
    return userRoleAssignments;
};

/// Admin
export const fetchApplicationAdmin = async (
    applicationAdminId: number | undefined
): Promise<FamAppAdminGet[]> => {
    console.log('1')
    if (!applicationAdminId) return [];
    console.log('2')
    console.log(applicationAdminId)
    const applicationAdmin = (
        await AdminMgmtApiService.applicationAdminApi.getApplicationAdminByApplicationId (
            applicationAdminId
        )
    ).data;



    console.log(applicationAdmin)

    // Default sorting
    // applicationAdmin.sort((first, second) => {
    //     console.log('3')

    //     // By user_name
    //     const userNameCompare = first.user.user_name.localeCompare(
    //         second.user.user_name
    //     );

    //     return userNameCompare
    // });
    console.log('4')

    return applicationAdmin;
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
): Promise<FamApplicationUserRoleAssignmentGet[]> => {
    await AppActlApiService.userRoleAssignmentApi.deleteUserRoleAssignment(
        userRoleXrefId
    );

    // When deletion is successful, refresh (fetrch) for frontend state.
    return fetchUserRoleAssignments(applicationId);
};

export const fetchApplicationRoles = async (
    applicationId: number
) => {
    const applicationRoles = (
        await AppActlApiService.applicationsApi.getFamApplicationRoles(
            applicationId
        )
    ).data;
    return applicationRoles;
};
