import { ref } from "vue";
import type { AuthState } from "@/types/AuthTypes";

// Create the initial state
const currentAuthState: AuthState = {
    isAuthenticated: false,
    famLoginUser: null,
    cognitoUser: null,
    accessToken: null,
    idToken: null,
    refreshToken: null,
    isAuthRestored: false,
};

// Export the ref-wrapped state for use across components
export const authState = ref<AuthState>(currentAuthState);
