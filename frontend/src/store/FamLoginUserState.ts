import { AdminMgmtApiService } from '@/services/ApiServiceFactory';
import { CURRENT_SELECTED_APPLICATION_KEY } from '@/store/ApplicationState';
import { setRouteToastError } from '@/store/ToastState';
import type { CognitoUserSession } from 'amazon-cognito-identity-js';
import type { FamAuthGrantDto } from 'fam-admin-mgmt-api/model';
import { readonly, ref } from "vue";

const FAM_LOGIN_USER = 'famLoginUser';

export interface FamLoginUser {
    username?: string;
    displayName?: string;
    email?: string;
    idpProvider?: string;
    roles?: string[];
    authToken?: CognitoUserSession;
    accesses?: FamAuthGrantDto[];
}

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
}

const getUserAccess = () => {
    return state.value.famLoginUser?.accesses;
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
    hasAccessRole,
    storeFamUser,
    removeFamUser,
    refreshCachedUserAccess
};