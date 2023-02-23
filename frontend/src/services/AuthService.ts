import router from '@/router';
import type { CognitoUserSession } from 'amazon-cognito-identity-js';
import { Auth } from 'aws-amplify';
import { readonly, ref } from 'vue';

const FAM_LOGIN_USER = 'famLoginUser';

export interface FamLoginUser {
    username?: string;
    idpProvider?: string;
    roles?: string[];
    authToken?: CognitoUserSession;
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

function isLoggedIn(): boolean {
    const loggedIn = !!state.value.famLoginUser?.authToken; // TODO check if token expired later?
    return loggedIn;
}

async function login() {
    /*
        See Aws-Amplify documenation:
        https://docs.amplify.aws/lib/auth/social/q/platform/js/
        https://docs.amplify.aws/lib/auth/advanced/q/platform/js/#identity-pool-federation
    */
    Auth.federatedSignIn();
}

async function logout() {
    Auth.signOut();
    removeFamUser();
    console.log('User logged out.');
    router.push('/');
}

async function handlePostLogin() {
    return Auth.currentAuthenticatedUser()
        .then(async (_userData) => {
            await refreshToken();
        })
        .catch((error) => {
            console.log('Not signed in');
            console.log('Authentication Error:', error);
            return logout();
        });
}

/**
 * Amplify method currentSession() will automatically refresh the accessToken and idToken
 * if tokens are "expired" and a valid refreshToken presented.
 *   // console.log("currentAuthToken: ", currentAuthToken)
 *   // console.log("ID Token: ", currentAuthToken.getIdToken().getJwtToken())
 *   // console.log("Access Token: ", currentAuthToken.getAccessToken().getJwtToken())
 *
 * Automatically logout if unable to get currentSession().
 */
async function refreshToken(): Promise<FamLoginUser | undefined> {
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
}

/**
 * See OIDC Attribute Mapping mapping reference:
 *      https://github.com/bcgov/nr-forests-access-management/wiki/OIDC-Attribute-Mapping
 * Note, current user data return for 'userData.username' is matched to "cognito:username" on Cognito.
 * Which isn't what we really want to display. The display username is "custom:idp_username" from token.
 */
function parseToken(authToken: CognitoUserSession): FamLoginUser {
    const decodedIdToken = authToken.getIdToken().decodePayload();
    const decodedAccessToken = authToken.getAccessToken().decodePayload();
    const famLoginUser = {
        username: decodedIdToken['custom:idp_username'],
        idpProvider: decodedIdToken['identities']['providerName'],
        roles: decodedAccessToken['cognito:groups'],
        authToken: authToken,
    };
    return famLoginUser;
}

function removeFamUser() {
    storeFamUser(undefined);
}

function storeFamUser(famLoginUser: FamLoginUser | null | undefined) {
    state.value.famLoginUser = famLoginUser;
    if (famLoginUser) {
        localStorage.setItem(FAM_LOGIN_USER, JSON.stringify(famLoginUser));
    } else {
        localStorage.removeItem(FAM_LOGIN_USER);
    }
}

// -----

const methods = {
    login,
    handlePostLogin,
    logout,
    refreshToken,
    removeFamUser,
};

const getters = {
    isLoggedIn,
};

export default {
    state: readonly(state), // readonly to prevent direct state change; force it through methods if needed to.
    methods,
    getters,
};
