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
import { isNewAccessId } from './utils';

// --- Fetching data (from backend)

export const fetchUserRoleAssignments = async (
    applicationId: number | undefined,
    newUsersAccessId: string | string[] = []
): Promise<FamApplicationUserRoleAssignmentGet[]> => {
    const convertedNewAppAdminId = newUsersAccessId
        ? Number(newUsersAccessId)
        : undefined;

    if (!applicationId) return [];

    const userRoleAssignments = (
        await AppActlApiService.applicationsApi.getFamApplicationUserRoleAssignment(
            applicationId
        )
    ).data;

    const alphabeticallySortedUsers = userRoleAssignments
        .slice()
        .sort((first, second) => {
            return first.user.user_name.localeCompare(second.user.user_name);
        });

    const newUserAccessSorted = alphabeticallySortedUsers
        .slice()
        .sort((first, second) => {
            const firstIsNew = isNewAccessId(
                convertedNewAppAdminId!,
                first.user_role_xref_id
            );
            const secondIsNew = isNewAccessId(
                convertedNewAppAdminId!,
                second.user_role_xref_id
            );

            if (firstIsNew && !secondIsNew) return -1;
            if (!firstIsNew && secondIsNew) return 1;
            return 0;
        });

    return newUserAccessSorted;
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
            const firstIsNew = isNewAccessId(
                convertedNewAppAdminId!,
                first.application_admin_id
            );
            const secondIsNew = isNewAccessId(
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
    applicationId: number | undefined,
    newDelegatedAdminsAccessId: string | string[] = []
): Promise<FamAccessControlPrivilegeGetResponse[]> => {
    if (!applicationId || !FamLoginUserState.isAdminOfSelectedApplication()) {
        return [];
    }

    const convertedDelegatedAdminsAccessId = newDelegatedAdminsAccessId
        ? Number(newDelegatedAdminsAccessId)
        : undefined;

    const delegatedAdmins = (
        await AdminMgmtApiService.delegatedAdminApi.getAccessControlPrivilegesByApplicationId(
            applicationId!
        )
    ).data;
    const alphabeticallySortedDelegatedAdmins = delegatedAdmins
        .slice()
        .sort((first, second) => {
            return first.user.user_name.localeCompare(second.user.user_name);
        });

    const newDelegatedAdminsSorted = alphabeticallySortedDelegatedAdmins
        .slice()
        .sort((first, second) => {
            const firstIsNew = isNewAccessId(
                convertedDelegatedAdminsAccessId!,
                first.access_control_privilege_id
            );
            const secondIsNew = isNewAccessId(
                convertedDelegatedAdminsAccessId!,
                second.access_control_privilege_id
            );

            if (firstIsNew && !secondIsNew) return -1;
            if (!firstIsNew && secondIsNew) return 1;
            return 0;
        });

    return newDelegatedAdminsSorted;
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
