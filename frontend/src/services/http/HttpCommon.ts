import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import HttpReqInterceptors from '@/services/http/HttpRequestInterceptors';
import HttpResInterceptors from '@/services/http/HttpResponseInterceptors';
import LoadingState from '@/store/LoadingState';
import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios';

const environmentSettings = new EnvironmentSettings();
const apiBaseUrl = environmentSettings.getApiBaseUrl();
const DEFAULT_CONTENT_TYPE = 'application/json';
const DEFAULT_REQUEST_TIMEOUT = 20000;

const defaultAxiosConfig = {
    baseURL: apiBaseUrl,
    timeout: DEFAULT_REQUEST_TIMEOUT,
    /*
    Note! This is the default status handling from Axios. Any status other than 2xx will be rejected,
          and does not show up at Promise 'then(response)' block. We coiuld configure below to change
          its behaviour.

        validateStatus: function (status) {
            return status >= 200 && status < 300; // default
        },
    */
};

// Use instance
const httpInstance = axios.create(defaultAxiosConfig);

// Common default settings, but individual request will take precedence.
httpInstance.defaults.headers.get['Content-type'] = DEFAULT_CONTENT_TYPE;

/*
  Private functions "loadingStart" "loadingStop" and "loadingStopWhenError" 
  are auxiliary special helpers for both request/response interceptors.

  When http request happens => assign isLoading state with true.
  When http response received or error happens =>  assign isLoading state with false
*/
const loadingStart = (config: AxiosRequestConfig) => {
    LoadingState.isLoading.value = true;
    return config;
};

const loadingStop = (res: AxiosResponse) => {
    LoadingState.isLoading.value = false;
    return res;
};

const loadingStopWhenError = (err: any) => {
    LoadingState.isLoading.value = false;
    return Promise.reject(err); // Based on Axios, return reject(err)
};

// Request Interceptors - note, last one is the first in execution sequence.
httpInstance.interceptors.request.use(HttpReqInterceptors.addAuthHeaderItcpt);
httpInstance.interceptors.request.use(loadingStart, loadingStopWhenError);

// Response Interceptors
httpInstance.interceptors.response.use(
    (response) => response,
    HttpResInterceptors.authenticationErrorResponsesItcpt
); // 401 error handler
httpInstance.interceptors.response.use(loadingStop, loadingStopWhenError);

export default httpInstance;
