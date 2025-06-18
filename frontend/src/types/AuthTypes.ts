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
    readonly isAuthRestored: boolean;
};

export interface AuthContext {
    authState: AuthState;
    login: (idp: IdpTypes) => Promise<void>;
    logout: () => Promise<void>;
    handlePostLogin: () => Promise<void>;
}
