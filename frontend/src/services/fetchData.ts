import type {
    FamAppAdminGetResponse,
    FamAccessControlPrivilegeGetResponse,
} from 'fam-admin-mgmt-api/model';
import type { FamApplicationUserRoleAssignmentGet } from 'fam-app-acsctl-api';
import {
    AppActlApiService,
    AdminMgmtApiService,
} from '@/services/ApiServiceFactory';
import FamLoginUserState from '@/store/FamLoginUserState';
import { selectedApplicationId } from '@/store/ApplicationState';
import { isNewAppAdminAccess } from './utils';

// --- Fetching data (from backend)

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

/**
 * This will call api to delete userRoleXrefId record from backend and fetch again
 * to refresh the state.
 * @param userRoleXrefId id to delete fam_user_role_assignment record.
 * @param applicationId id to fetch and refresh fam_user_role_assignment records with the applicationId.
 */
export const deleteAndRefreshUserRoleAssignments = async (
    userRoleXrefId: number,
    applicationId: number
): Promise<FamApplicationUserRoleAssignmentGet[]> => {
    await AppActlApiService.userRoleAssignmentApi.deleteUserRoleAssignment(
        userRoleXrefId
    );

    // When deletion is successful, refresh (fetrch) for frontend state.
    return fetchUserRoleAssignments(applicationId);
};

export const fetchApplicationAdmins = async (
    newAppAdminId: any = undefined
): Promise<FamAppAdminGetResponse[]> => {
    const convertedNewAppAdminId = newAppAdminId
        ? Number(newAppAdminId)
        : undefined;
    const applicationAdmins = (
        await AdminMgmtApiService.applicationAdminApi.getApplicationAdmins()
    ).data;

    const alphabeticallySortedAdmins = applicationAdmins
        .slice()
        .sort((first, second) => {
            return first.user.user_name.localeCompare(second.user.user_name);
        });

    const newAdminsAccesSorted = alphabeticallySortedAdmins
        .slice()
        .sort((first, second) => {
            const firstIsNew = isNewAppAdminAccess(
                convertedNewAppAdminId!,
                first.application_admin_id
            );
            const secondIsNew = isNewAppAdminAccess(
                convertedNewAppAdminId!,
                second.application_admin_id
            );

            if (firstIsNew && !secondIsNew) return -1;
            if (!firstIsNew && secondIsNew) return 1;
            return 0;
        });
    return newAdminsAccesSorted;
};

/**
 * This will call api to delete applicationAdminId record from backend and fetch again
 * to refresh the state.
 * @param applicationAdminId id to delete fam_user_role_assignment record.
 */
export const deleteAndRefreshApplicationAdmin = async (
    applicationAdminId: number
): Promise<FamAppAdminGetResponse[]> => {
    await AdminMgmtApiService.applicationAdminApi.deleteApplicationAdmin(
        applicationAdminId
    );
    // When deletion is successful, refresh (fetch) for frontend state.
    return fetchApplicationAdmins();
};

export const fetchDelegatedAdmins = async (
    applicationId: number | undefined
): Promise<FamAccessControlPrivilegeGetResponse[]> => {
    if (!applicationId || !FamLoginUserState.isAdminOfSelectedApplication()) {
        return [];
    }

    const delegatedAdmins = (
        await AdminMgmtApiService.delegatedAdminApi.getAccessControlPrivilegesByApplicationId(
            applicationId!
        )
    ).data;

    // Default sorting
    delegatedAdmins.sort((first, second) => {
        // By user_name
        const userNameCompare = first.user.user_name.localeCompare(
            second.user.user_name
        );

        return userNameCompare;
    });

    return delegatedAdmins;
};

/**
 * This will call api to delete delegatedAdminPrivilege record from backend and fetch again
 * to refresh the state.
 * @param accessPrivilegegId id to delete delegated admin accesss record.
 */
export const deleteAndRefreshDelegatedAdmin = async (
    accessPrivilegegId: number
): Promise<FamAccessControlPrivilegeGetResponse[]> => {
    await AdminMgmtApiService.delegatedAdminApi.deleteAccessControlPrivilege(
        accessPrivilegegId
    );
    // When deletion is successful, refresh (fetch) for frontend state.
    return fetchDelegatedAdmins(selectedApplicationId.value);
};
