import { readonly, ref } from 'vue';
import { Auth } from 'aws-amplify';
import type { CognitoUserSession } from 'amazon-cognito-identity-js';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import { CURRENT_SELECTED_APPLICATION_KEY } from '@/store/ApplicationState';
import { setRouteToastError } from '@/store/ToastState';
import { AdminMgmtApiService } from '@/services/ApiServiceFactory';
import type { FamAuthGrantDto } from 'fam-admin-mgmt-api/model';

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

// functions

const isLoggedIn = (): boolean => {
    const loggedIn = !!state.value.famLoginUser?.authToken; // TODO check if token expired later?
    return loggedIn;
};

const login = async () => {
    /*
        See Aws-Amplify documenation:
        https://docs.amplify.aws/lib/auth/social/q/platform/js/
        https://docs.amplify.aws/lib/auth/advanced/q/platform/js/#identity-pool-federation
    */

    const environmentSettings = new EnvironmentSettings();

    Auth.federatedSignIn({
        customProvider: environmentSettings.getIdentityProvider(),
    });
};

const logout = async () => {
    Auth.signOut();
    removeFamUser();
    console.log('User logged out.');
};

const handlePostLogin = async () => {
    try {
        await Auth.currentAuthenticatedUser();
        await refreshToken();
        await getUserAccess();
    } catch (error) {
        console.log('Not signed in');
        console.log('Authentication Error:', error);
        logout();
    }
};

const getUserAccess = async () => {
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

/**
 * Amplify method currentSession() will automatically refresh the accessToken and idToken
 * if tokens are "expired" and a valid refreshToken presented.
 *   // console.log("currentAuthToken: ", currentAuthToken)
 *   // console.log("ID Token: ", currentAuthToken.getIdToken().getJwtToken())
 *   // console.log("Access Token: ", currentAuthToken.getAccessToken().getJwtToken())
 *
 * Automatically logout if unable to get currentSession().
 */
const refreshToken = async (): Promise<FamLoginUser | undefined> => {
    try {
        console.log('Refreshing Token...');
        const currentAuthToken: CognitoUserSession =
            await Auth.currentSession();
        console.log('currentAuthToken: ', currentAuthToken);

        const famLoginUser = parseToken(currentAuthToken);
        storeFamUser(famLoginUser);
        return famLoginUser;
    } catch (error) {
        console.error(
            'Problem refreshing token or token is invalidated:',
            error
        );
        // logout and redirect to login.
        logout();
    }
};

/**
 * See OIDC Attribute Mapping mapping reference:
 *      https://github.com/bcgov/nr-forests-access-management/wiki/OIDC-Attribute-Mapping
 * Note, current user data return for 'userData.username' is matched to "cognito:username" on Cognito.
 * Which isn't what we really want to display. The display username is "custom:idp_username" from token.
 */
const parseToken = (authToken: CognitoUserSession): FamLoginUser => {
    const decodedIdToken = authToken.getIdToken().decodePayload();
    const decodedAccessToken = authToken.getAccessToken().decodePayload();
    const famLoginUser = {
        username: decodedIdToken['custom:idp_username'],
        displayName: decodedIdToken['custom:idp_display_name'],
        email: decodedIdToken['email'],
        idpProvider: decodedIdToken['identities']['providerName'],
        roles: decodedAccessToken['cognito:groups'],
        authToken: authToken,
    };
    return famLoginUser;
};

const removeFamUser = () => {
    storeFamUser(undefined);
    // clean up local storage for selected application
    localStorage.removeItem(CURRENT_SELECTED_APPLICATION_KEY);
};

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

const hasAccessRole = (role: string): boolean => {
    if (state.value.famLoginUser?.roles?.includes(role)) {
        return true;
    }
    return false;
};

// -----

const methods = {
    login,
    handlePostLogin,
    logout,
    refreshToken,
    removeFamUser,
    hasAccessRole,
    getUserAccess
};

const getters = {
    isLoggedIn,
};

export default {
    state: readonly(state), // readonly to prevent direct state change; force it through methods if needed to.
    methods,
    getters,
};
