
import authService from '@/services/AuthService';
import type { AxiosRequestConfig } from 'axios';

// Typically when adding "request" interceptors, they are presumed to be asynchronous by default.
// See "https://www.npmjs.com/package/axios#interceptors" if there is a need for synchronous interceptors behaviour.

function addAuthHeaderItcpt(config: AxiosRequestConfig) {
    const authToken = authService.state.value.famLoginUser?.authToken
    if (authToken) {
        const authHeader = `Bearer ${authToken.getAccessToken().getJwtToken()}`
        const idTokenHeader = authToken.getIdToken().getJwtToken()
        config.headers? (config.headers['Authorization'] = authHeader, config.headers['id-token'] = idTokenHeader)
                      : (config.headers = {'Authorization': authHeader}, {'id-token': idTokenHeader})
    }
    return config
}


export default {
    addAuthHeaderItcpt
}