import useAuth from "@/composables/useAuth";
import type { InternalAxiosRequestConfig } from "axios";

/**
 * Adds the authorization header to the Axios request configuration.
 * Retrieves the access token from the auth state and adds it as a Bearer token.
 *
 * @param {InternalAxiosRequestConfig} config - The Axios request configuration object.
 * @returns {InternalAxiosRequestConfig} The modified request configuration with the Authorization header.
 */
const attachAuthHeader = (
    config: InternalAxiosRequestConfig
): InternalAxiosRequestConfig => {
    const auth = useAuth();
    const accessToken = auth.authState.accessToken?.getJwtToken();
    if (accessToken) {
        const authHeader = `Bearer ${accessToken}`;
        config.headers.setAuthorization(authHeader);
    }
    return config;
};

export default {
    attachAuthHeader,
};
