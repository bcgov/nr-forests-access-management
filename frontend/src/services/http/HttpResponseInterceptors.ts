import AuthService from "@/services/AuthService";
import Http from '@/services/http/HttpCommon';
import type { AxiosRequestConfig, AxiosResponse } from "axios";
import { ref } from 'vue';
import router from '../../router';

/*
Note! Any status other than 2xx will be rejected (default status handling from Axios unless changed).
*/

const retryCount = ref(0)
const MAX_RETRY = 2

// --- Interceptors

// Assume it is caught in error block based on default handling.
// 401 Interceptor
async function authenticationErrorResponsesItcpt(error: any) {
    // Special handling; until MAX_RETRY reached.
    if (error.response?.status == 401) {
        if ((retryCount.value < MAX_RETRY)) {
            return refreshTokenAndReTry(error.config, error.response);
        }
        AuthService.methods.removeFamUser() // Done retry refresh token, token expired; remove user.
    }

    retryCount.value = 0 // reset counter when retry ends or not 401.
    return Promise.reject(error); // return error for next interceptor.
}

// 403 Interceptor
async function forbiddenErrorResponseItcpt(error: any) {
    if (error.response?.status == 403) {
        router.replace('/') // Unauthorized operation, direct back to home.
    }
    return Promise.reject(error);
}

async function refreshTokenAndReTry(config: AxiosRequestConfig, response: AxiosResponse) {
    // Refresh token.
    await AuthService.methods.refreshToken()

    // Try original request again.
    retryCount.value++
    return Http.request(config)
        .catch((error) => {
            console.log("Still encountered error after request retried: ", error)
            return Promise.reject(error);
        })
}

export default {
    authenticationErrorResponsesItcpt,
    forbiddenErrorResponseItcpt
}