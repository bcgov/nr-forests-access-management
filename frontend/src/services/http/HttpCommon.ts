import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import HttpReqInterceptors from '@/services/http/HttpRequestInterceptors';
import axios from 'axios';

const environmentSettings = new EnvironmentSettings()
const apiBaseUrl = environmentSettings.getApiBaseUrl()
const DEFAULT_CONTENT_TYPE = 'application/json';
const DEFAULT_REQUEST_TIMEOUT = 5000;

const defaultAxiosConfig = {
    baseURL: apiBaseUrl,
    timeout: DEFAULT_REQUEST_TIMEOUT,
};

// Use instance
const httpInstance = axios.create(defaultAxiosConfig);

// Common default, but individual request will take precedence.
httpInstance.defaults.headers.get['Content-type'] = DEFAULT_CONTENT_TYPE;

// Request Interceptors
httpInstance.interceptors.request.use(HttpReqInterceptors.addAuthHeaderItcpt);


export default httpInstance;