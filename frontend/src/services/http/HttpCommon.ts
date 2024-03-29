import HttpReqInterceptors from '@/services/http/HttpRequestInterceptors';
import HttpResInterceptors from '@/services/http/HttpResponseInterceptors';
import { setLoadingState } from '@/store/LoadingState';
import axios, { type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';

const DEFAULT_CONTENT_TYPE = 'application/json';
const DEFAULT_REQUEST_TIMEOUT = 20000;

/**
 * // `baseURL` setting is removed from default axios config.
 * For the current vesion of axios, if this is set during the `axios.create(defaultAxiosConfig)`, it can't be overridden
 * from the later reuqest's option passing in. FAM currently has more than one API(s) baseURL(s), leave this `baseURL`
 * to be configured when API service(s) are instantiated.
 */
const defaultAxiosConfig = {
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

  When http request happens => assign LoadingState state with true.
  When http response received or error happens =>  assign LoadingState state with false
*/
const loadingStart = (config: InternalAxiosRequestConfig) => {
    setLoadingState(true);
    return config;
};

const loadingStop = (res: AxiosResponse) => {
    setLoadingState(false);
    return res;
};

const loadingStopWhenError = (err: any) => {
    setLoadingState(false);
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
