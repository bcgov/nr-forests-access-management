
import authService from '@/services/AuthService';
import type { AxiosRequestConfig } from 'axios';

// Typically when adding "request" interceptors, they are presumed to be asynchronous by default.
// See "https://www.npmjs.com/package/axios#interceptors" if there is a need for synchronous interceptors behaviour.

function addAuthHeaderItcpt(config: AxiosRequestConfig) {
    const token = authService.state.value.famLoginUser?.token
    if (token) {
        const authHeader = `Bearer ${JSON.stringify(token)}`
        config.headers? config.headers['Authorization'] = authHeader
                      : config.headers = {'Authorization': authHeader}
        console.log(`Auth header added: ${config.headers['Authorization']}`)
    }
    return config
}


export default { 
    addAuthHeaderItcpt
}