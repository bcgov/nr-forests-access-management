import type {
    CognitoUser,
    CognitoAccessToken,
    CognitoIdToken,
    CognitoRefreshToken,
} from "amazon-cognito-identity-js";

import type { IdpProvider } from "@/enum/IdpEnum";

export type IdpTypes = IdpProvider.IDIR | IdpProvider.BCEIDBUSINESS;

export type FamLoginUser = {
    username?: string;
    displayName?: string;
    email?: string;
    idpProvider?: string;
    organization?: string;
};

export type AuthState = {
    readonly isAuthenticated: boolean;
    readonly famLoginUser: FamLoginUser | null;
    readonly cognitoUser: CognitoUser | null;
    readonly accessToken: CognitoAccessToken | null;
    readonly idToken: CognitoIdToken | null;
    readonly refreshToken: CognitoRefreshToken | null;
};

export interface AuthContext {
    authState: AuthState;
    login: (idp: IdpTypes) => Promise<void>;
    logout: () => Promise<void>;
    handlePostLogin: () => Promise<void>;
}
