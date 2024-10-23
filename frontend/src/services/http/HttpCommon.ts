import axios from "axios";
import HttpReqInterceptors from "@/services/http/HttpRequestInterceptors";
import { FIFTEEN_SECONDS } from "@/constants/TimeUnits";

const DEFAULT_CONTENT_TYPE = "application/json";
const DEFAULT_REQUEST_TIMEOUT = FIFTEEN_SECONDS;

const defaultAxiosConfig = {
    timeout: DEFAULT_REQUEST_TIMEOUT,
};

// Create an Axios instance with the default configuration
const httpInstance = axios.create(defaultAxiosConfig);

// Common default settings, but individual request will take precedence.
httpInstance.defaults.headers.get["Content-type"] = DEFAULT_CONTENT_TYPE;

// Request Interceptors - note, last one is the first in execution sequence.
httpInstance.interceptors.request.use(HttpReqInterceptors.attachAuthHeader);

export default httpInstance;
