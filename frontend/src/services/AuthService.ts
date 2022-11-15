import router from '@/router';
import { readonly, ref } from 'vue';
import { Auth } from 'aws-amplify';
import type { CognitoUserSession } from 'amazon-cognito-identity-js';

const FAM_LOGIN_USER = 'famLoginUser'

export interface FamLoginUser {
    username: string,
    token: any
}

const state = ref({
    famLoginUser: localStorage.getItem(FAM_LOGIN_USER)? 
                    JSON.parse(localStorage.getItem(FAM_LOGIN_USER) as string) as (FamLoginUser | undefined | null)
                    : undefined,
})

// functions

function isLoggedIn(): boolean {
    const loggedIn = !!state.value.famLoginUser?.token; // TODO check if token expired later?
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
    Auth.signOut()
    storeFamUser(undefined)
    console.log("User logged out.")
    router.push('/')
}

async function handlePostLogin() {
    return Auth.currentAuthenticatedUser()
        .then(async (userData) => {
            await refreshToken()
        })
        .catch((error) => {
            console.log('Not signed in')
            console.log('Authentication Error:', error)
            return logout()
        });
}

/**
 * Amplify method currentSession() will automatically refresh the accessToken and idToken 
 * if tokens are expired and a valid refreshToken presented.
 * 
 * Automatically logout if unable to get currentSession().
 */
async function refreshToken(): Promise<FamLoginUser | undefined> {
    try {
        console.log("Refreshing Token...")
        const refreshedToken: CognitoUserSession = await Auth.currentSession()
        
        // Note, current user data return for 'userData.username' is matched to "cognito:username" on Cognito.
        // Which isn't what we really want to display. The display username is "custom:idp_username" from token.
        const famLoginUser = {
            username: refreshedToken.getIdToken().decodePayload()['custom:idp_username'],
            token: refreshedToken
        };
        storeFamUser(famLoginUser)
        return famLoginUser;
    }
    catch(error) {
        console.error("Problem refreshing token or token is invalidated:", error)
        // logout and redirect to login.
        logout()
    }
}

function storeFamUser(famLoginUser: FamLoginUser | null | undefined) {
    state.value.famLoginUser = famLoginUser
    if (famLoginUser) {
        localStorage.setItem(FAM_LOGIN_USER, JSON.stringify(famLoginUser))
    }
    else {
        localStorage.removeItem(FAM_LOGIN_USER)
    }
}

// -----

const methods = {
    login,
    handlePostLogin,
    logout,
    refreshToken
}

const getters = {
    isLoggedIn
}

export default {
    state: readonly(state), // readonly to prevent direct state change; force it through methods if needed to.
    methods,
    getters 
}