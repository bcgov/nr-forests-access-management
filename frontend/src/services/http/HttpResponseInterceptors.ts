import AuthService from "@/services/AuthService";
import Http from '@/services/http/HttpCommon';
import type { AxiosResponse } from "axios";
import { ref } from 'vue';
import router from '../../router';

/*
Note! Any status other than 2xx will be rejected (default status handling from Axios unless changed).
*/

const retryCount = ref(0)
const MAX_RETRY = 2

// --- Interceptors

// Assume it is caught in error block based on default handling.
async function accessErrorResponsesItcpt(error: any) {
    if(error.response.status == 401) {
        router.push('/')
        return Promise.reject(error);
    }
    // 403 special handling; until MAX_RETRY reached.
    if(error.response.status == 403 && (retryCount.value < MAX_RETRY)) {
        return refreshTokenAndReTry(error.request.responseURL, error.response);
    }

    retryCount.value = 0 // reset counter when retry ends or not 403.
    return Promise.reject(error);
}

async function refreshTokenAndReTry(request: any, response: AxiosResponse) {
    // Refresh token.
    await AuthService.methods.refreshToken()

    // Try original request again.
    retryCount.value++
    return Http.request(request)
    .catch((error) => {
        console.log("Still encountered error after request retried: ", error)
        return Promise.reject(error);
    })
}

export default {
    accessErrorResponsesItcpt
}