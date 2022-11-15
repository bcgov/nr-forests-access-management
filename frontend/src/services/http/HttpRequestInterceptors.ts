
import authService from '@/services/AuthService';

// Typically when adding "request" interceptors, they are presumed to be asynchronous by default.
// See "https://www.npmjs.com/package/axios#interceptors" if there is a need for synchronous interceptors behaviour.

function addAuthHeaderItcpt(config: any) {
    const token = authService.state.value.famLoginUser?.token;
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
}


export default { 
    addAuthHeaderItcpt
}