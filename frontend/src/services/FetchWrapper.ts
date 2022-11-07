import authService from '@/services/AuthService';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';

const DEFAULT_CONTENT_TYPE = 'application/json';

/**
 * Wrapping Fetch calls: for adding auth header and intercept request/response if needed for system level.
 */
export const fetchWrapper = {
    get: request('GET'),
    post: request('POST'),
    put: request('PUT'),
    delete: request('DELETE')
};

function request(method: string) {
    return async (url: string, body?: any, headerObj?: any) => {
        const requestOptions = {
            method,
            headers: addAuthHeader(url, headerObj),
            body
        };
        if (!requestOptions.headers['Content-Type']){
            requestOptions.headers['Content-Type'] = DEFAULT_CONTENT_TYPE;
        }

        if (body) {
            requestOptions.body = JSON.stringify(body);
        }

        console.log('Request with requestOptions:', requestOptions)
        console.log('Request with body', body)
        return fetch(url, requestOptions).then(handleResponse);
    }
}

// helper functions

function addAuthHeader(url: string, headerObj?: any): any {
    const environmentSettings = new EnvironmentSettings()
    const apiBaseUrl = environmentSettings.getApiBaseUrl()

    const headers = headerObj? headerObj: {};
    const isLoggedIn = authService.getters.isLoggedIn();
    const isApiUrl = url.startsWith(apiBaseUrl);

    // TODO: Do we need this restriction on if the request is to go to api? The frontend app only calls api anyway, right?
    if (isLoggedIn && isApiUrl) {
        // Add 'Bearer' token.
        headers['Authorization'] = `Bearer ${authService.state.famUser.token}`;
    }
    console.log(`headers: `, headers)
    return headers;
}

async function handleResponse(response: Response) {
    const data = await response.json(); console.log('data: ', data);
    const { famUser } = authService.state;
    if (!response.ok) {
        if ([401, 403].includes(response.status) && famUser) {
            // auto logout if 401 Unauthorized or 403 Forbidden response returned from api.
            // TODO, later might need to refresh jwt token.
            authService.methods.logout();
        }

        const error = (data && data.message) || response.statusText;
        return Promise.reject(error);
    }
    return data;
}