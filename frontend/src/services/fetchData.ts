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
import { isNewAccess } from './utils';

// --- Fetching data (from backend)

export const fetchUserRoleAssignments = async (
    applicationId: number | undefined,
    newUserAccessIds: string = ''
): Promise<FamApplicationUserRoleAssignmentGet[]> => {
    if (!applicationId) return [];

    const newUsersAccessIdsList = newUserAccessIds.split(',');

    const userRoleAssignments = (
        await AppActlApiService.applicationsApi.getFamApplicationUserRoleAssignment(
            applicationId
        )
    ).data;

    userRoleAssignments.sort((first, second) => {
        const firstIsNew = isNewAccess(
            newUsersAccessIdsList,
            first.user_role_xref_id
        );
        const secondIsNew = isNewAccess(
            newUsersAccessIdsList,
            second.user_role_xref_id
        );

        if (firstIsNew && !secondIsNew) return -1;
        if (!firstIsNew && secondIsNew) return 1;

        return first.user.user_name.localeCompare(second.user.user_name);
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
    newAppAdminId: string = ''
): Promise<FamAppAdminGetResponse[]> => {
    const newAppAdminIdsList = newAppAdminId.split(',');

    const applicationAdmins = (
        await AdminMgmtApiService.applicationAdminApi.getApplicationAdmins()
    ).data;

    applicationAdmins.sort((first, second) => {
        const firstIsNew = isNewAccess(
            newAppAdminIdsList,
            first.application_admin_id
        );
        const secondIsNew = isNewAccess(
            newAppAdminIdsList,
            second.application_admin_id
        );

        if (firstIsNew && !secondIsNew) return -1;
        if (!firstIsNew && secondIsNew) return 1;

        return first.user.user_name.localeCompare(second.user.user_name);
    });

    return applicationAdmins;
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
    applicationId: number | undefined,
    newDelegatedAdminIds: string = ''
): Promise<FamAccessControlPrivilegeGetResponse[]> => {
    if (!applicationId || !FamLoginUserState.isAdminOfSelectedApplication()) {
        return [];
    }

    const newDelegatedAdminIdsList = newDelegatedAdminIds.split(',');

    const delegatedAdmins = (
        await AdminMgmtApiService.delegatedAdminApi.getAccessControlPrivilegesByApplicationId(
            applicationId
        )
    ).data;

    delegatedAdmins.sort((first, second) => {
        const firstIsNew = isNewAccess(
            newDelegatedAdminIdsList,
            first.access_control_privilege_id
        );
        const secondIsNew = isNewAccess(
            newDelegatedAdminIdsList,
            second.access_control_privilege_id
        );

        if (firstIsNew && !secondIsNew) return -1;
        if (!firstIsNew && secondIsNew) return 1;

        return first.user.user_name.localeCompare(second.user.user_name);
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
