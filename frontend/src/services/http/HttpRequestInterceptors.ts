import authService from '@/services/AuthService';
import type { AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';

// Typically when adding "request" interceptors, they are presumed to be asynchronous by default.
// See "https://www.npmjs.com/package/axios#interceptors" if there is a need for synchronous interceptors behaviour.

function addAuthHeaderItcpt(config: InternalAxiosRequestConfig) {
    const authToken = authService.state.value.famLoginUser?.authToken;
    if (authToken) {
        const authHeader = `Bearer ${authToken.getAccessToken().getJwtToken()}`;
        config.headers.setAuthorization(authHeader)
    }
    return config;
}

export default {
    addAuthHeaderItcpt,
};
