import { hashRouter } from '@/router';
import AuthService from '@/services/AuthService';
import Http from '@/services/http/HttpCommon';
import LoginUserState from '@/store/FamLoginUserState';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';
import { ref } from 'vue';

/*
Note! Any status other than 2xx will be rejected (default status handling from Axios unless changed).
*/

const retryCount = ref(0);
const MAX_RETRY = 2;

// --- Interceptors

// Assume it is caught in error block based on default handling.
// 401 Interceptor
async function authenticationErrorResponsesItcpt(error: any) {
    // Special handling; until MAX_RETRY reached.
    if (error.response?.status == 401) {
        if (retryCount.value < MAX_RETRY) {
            try {
                return await refreshTokenAndReTry(error.config, error.response);
            } catch (error) {
                return Promise.reject(error);
            }
        } else {
            LoginUserState.removeFamUser(); // Done retry refresh token, token expired; remove user.
            hashRouter.replace('/'); // 401 unauthenticated/expired, back to home page.
        }
    }
    retryCount.value = 0; // Reset counter when retry ends or not 401.
    return Promise.reject(error); // return error for next interceptor.
}

async function refreshTokenAndReTry(
    config: AxiosRequestConfig,
    response: AxiosResponse
) {
    // Refresh token.
    await AuthService.refreshToken();

    // Try original request again.
    retryCount.value++;
    return Http.request(config)
        .then((response) => {
            retryCount.value = 0; // Reset retryCount when retried request does come through successfully.
            return Promise.resolve(response); // Pass to next in response chain.
        })
        .catch((error) => {
            console.log(
                'Still encountered error after request retried: ',
                error
            );
            return Promise.reject(error);
        });
}

export default {
    authenticationErrorResponsesItcpt,
};
