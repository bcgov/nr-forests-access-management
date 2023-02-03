import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import HttpReqInterceptors from '@/services/http/HttpRequestInterceptors';
import HttpResInterceptors from '@/services/http/HttpResponseInterceptors';
import axios from 'axios';

const environmentSettings = new EnvironmentSettings()
const apiBaseUrl = environmentSettings.getApiBaseUrl()
const DEFAULT_CONTENT_TYPE = 'application/json';
const DEFAULT_REQUEST_TIMEOUT = 5000;

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

// Request Interceptors
httpInstance.interceptors.request.use(HttpReqInterceptors.addAuthHeaderItcpt);

// Response Interceptors
httpInstance.interceptors.response.use(response => response, HttpResInterceptors.accessErrorResponsesItcpt); // Provide error block handling.



export default httpInstance;