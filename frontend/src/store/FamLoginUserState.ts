import { AdminMgmtApiService } from '@/services/ApiServiceFactory';
import { CURRENT_SELECTED_APPLICATION_KEY } from '@/store/ApplicationState';
import { FAM_APPLICATION_NAME } from '@/store/Constants';
import { setRouteToastError } from '@/store/ToastState';
import type { CognitoUserSession } from 'amazon-cognito-identity-js';
import { AdminRoleAuthGroup, type FamApplicationDto, type FamAuthGrantDto } from 'fam-admin-mgmt-api/model';
import { readonly, ref } from "vue";

const FAM_LOGIN_USER = 'famLoginUser';

// For some of the values of the FAMLoginUser properties, see AuthService.parseToken().
export interface FamLoginUser {
    username?: string;
    displayName?: string;
    email?: string;
    idpProvider?: string; // from ID Token's ['identities']['providerName'] attribute.
    roles?: string[]; // roles from Access Token's ['cognito:groups']. This may soon be redundant after delegated admin design.
    authToken?: CognitoUserSession; // original JWT token from AWS Cognito (ID && Access Tokens).
    accesses?: FamAuthGrantDto[]; // admin privileges retrieved from backend.
};

const state = ref({
    famLoginUser: localStorage.getItem(FAM_LOGIN_USER)
        ? (JSON.parse(localStorage.getItem(FAM_LOGIN_USER) as string) as
              | FamLoginUser
              | undefined
              | null)
        : undefined,
});

// --- getters

const getAuthToken = () => {
    return state.value.famLoginUser?.authToken;
};

const getUserAccess = () => {
    return state.value.famLoginUser?.accesses;
};

// admin levels: 'FAM_ADMIN', 'APP_ADMIN', 'DELEGATED_ADMIN'
const getUserAdminRoleGroups = () => {
    const accesses = getUserAccess();
    if (accesses && accesses.length > 0) {
        return accesses.map(
            (access) => access.auth_key
        )
    }
};

/**
 * @param adminRole three admin levels: 'FAM_ADMIN', 'APP_ADMIN', 'DELEGATED_ADMIN'
 * @returns array of applications the login user has been granted for
 *          administering on based on adimn level.
 */
const getApplicationsAdministeredByAdminRole = (
    adminRole: AdminRoleAuthGroup
): FamApplicationDto[] | undefined => {
    const accesses = getUserAccess();
    if (accesses && accesses.length > 0) {
        const access = accesses.filter(
            (access) => access.auth_key == adminRole
        )[0]
        return access
            .grants
            .map((grant) => grant.application)
            .sort((first, second) => first.id - second.id);
    }
};

/**
 * Note!! this is to combine all applications the user has been granted
 * and can administer on with different admin level privileges, only for
 * special usage at dashboard page (ManagePermissions) since the user when
 * it lands on the first page it needs to select "application" first.
 *
 * If the way our forntend works is based on admin level to display
 * management table instead of selecting "applicatoin" first, it won't need
 * this particular function.
 */
const getApplicationsUserAdministers = () => {
    const userAdminRoleGroups = getUserAdminRoleGroups();
    let famApp;
    let applicationSet = new Set<FamApplicationDto>();
    if (userAdminRoleGroups) {
        userAdminRoleGroups.forEach(adminRoleGroup => {
            const apps = getApplicationsAdministeredByAdminRole(adminRoleGroup)
            if (adminRoleGroup == AdminRoleAuthGroup.FamAdmin) {
                famApp = apps!.filter((app) => app.name == FAM_APPLICATION_NAME)[0];
            }
            else {
                applicationSet = new Set([...applicationSet, ...apps!])
            }
        });

        const applications = new Array(...applicationSet);
        applications.sort((first, second) => first.id - second.id);
        if (famApp) applications.unshift(famApp); // add FAM to the first if FAM Admin.
        return applications;
    }
};

const hasAccessRole = (role: string): boolean => {
    if (state.value.famLoginUser?.roles?.includes(role)) {
        return true;
    }
    return false;
};

// --- setters

const storeFamUser = (famLoginUser: FamLoginUser | null | undefined) => {
    state.value.famLoginUser = famLoginUser;
    if (famLoginUser) {
        localStorage.setItem(
            FAM_LOGIN_USER,
            JSON.stringify(state.value.famLoginUser)
        );
    } else {
        localStorage.removeItem(FAM_LOGIN_USER);
    }
};

const removeFamUser = () => {
    storeFamUser(undefined);
    // clean up local storage for selected application
    localStorage.removeItem(CURRENT_SELECTED_APPLICATION_KEY);
};

/**
 * To refresh User granted privileges when neccssary.
 * FamLoginUser contains a property "accesses" that sometimes needs to be
 * refreshed and stored into localStorage at FamLoginUser object.
 */
const refreshCachedUserAccess = async () => {
    try {
        const userAccessData =
            await AdminMgmtApiService.adminUserAccessesApi.adminUserAccessPrivilege();
        state.value.famLoginUser!.accesses = userAccessData.data.access;
        storeFamUser(state.value.famLoginUser);
    } catch (error: any) {
        console.log("Unable to get user's access in FAM", error);
        setRouteToastError(error);
    }
};

// --- export

export default {
    state: readonly(state), // readonly to prevent direct state change; force it through functions if needed to.
    getAuthToken,
    getUserAccess,
    getUserAdminRoleGroups,
    getApplicationsAdministeredByAdminRole,
    getApplicationsUserAdministers,
    hasAccessRole,
    storeFamUser,
    removeFamUser,
    refreshCachedUserAccess
};