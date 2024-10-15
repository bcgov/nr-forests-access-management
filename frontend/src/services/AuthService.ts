import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import LoginUserState, { type FamLoginUser } from "@/store/FamLoginUserState";
import { showTermsForAcceptance } from "@/store/TermsAndConditionsState";
import type { CognitoUserSession } from "amazon-cognito-identity-js";
import { Auth } from "aws-amplify";

// functions

const isLoggedIn = (): boolean => {
    const loggedIn = !!LoginUserState.getAuthToken();
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
        customProvider: environmentSettings.getIdentityProviderIdir(),
    });
};

const loginBusinessBceid = async () => {
    const environmentSettings = new EnvironmentSettings();
    Auth.federatedSignIn({
        customProvider: environmentSettings.getIdentityProviderBceid(),
    });
};

const logout = async () => {
    await Auth.signOut();
    LoginUserState.removeFamUser();
    console.log("User logged out.");
};

const handlePostLogin = async () => {
    try {
        await Auth.currentAuthenticatedUser();
        await refreshToken();

        // This is to update the FamLoginUser for FamLoginUser.accesses.
        // For now team decided to grab user's access only when user login and may change later.
        await LoginUserState.cacheUserAccess();

        if (
            LoginUserState.state.value.famLoginUser?.accesses &&
            LoginUserState.state.value.famLoginUser.accesses.length > 0
        ) {
            // only check if user needs accept terms and conditions if is a FAM user
            (await LoginUserState.requiresAcceptTermsCondition()) &&
                showTermsForAcceptance();
        }
    } catch (error) {
        console.log("Not signed in");
        console.log("Authentication Error:", error);
        logout();
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
        console.log("Refreshing Token...");
        const currentAuthToken: CognitoUserSession =
            await Auth.currentSession();

        const famLoginUser = parseToken(currentAuthToken);

        // if there is and existing "accesses" for user, add it to FamLoginUser object.
        const accesses = LoginUserState.getUserAccess();
        if (accesses) famLoginUser.accesses = accesses;
        LoginUserState.storeFamUser(famLoginUser);
        return famLoginUser;
    } catch (error) {
        console.error(
            "Problem refreshing token or token is invalidated:",
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
    const famLoginUser = {
        username: decodedIdToken["custom:idp_username"],
        displayName: decodedIdToken["custom:idp_display_name"],
        email: decodedIdToken["email"],
        idpProvider: decodedIdToken["identities"][0]["providerName"],
        authToken: authToken,
        organization: decodedIdToken["custom:idp_business_name"],
    };
    return famLoginUser;
};

// -----

export default {
    login,
    loginBusinessBceid,
    isLoggedIn,
    handlePostLogin,
    logout,
    refreshToken,
};
