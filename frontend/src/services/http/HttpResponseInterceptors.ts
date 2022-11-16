
import AuthService from "@/services/AuthService";
import type { AxiosRequestConfig, AxiosResponse } from "axios";
/*
Note! Any status other than 2xx will be rejected (default status handling from Axios unless changed).
*/

// Assume it is caught in error block based on default handling.
async function forbiddenStatusItcpt(error: any) {
    // 403 special handling.
    if(error.response.status == 403) {
        await refreshTokenAndReTry(error.request, error.response);
    }
}

async function refreshTokenAndReTry(request: AxiosRequestConfig, response: AxiosResponse) {
    console.log("refreshing token...")
    // TODO implement in future.
}

export default { 
    forbiddenStatusItcpt
}