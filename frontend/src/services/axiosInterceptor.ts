import { fetchAuthSession, type AuthTokens } from 'aws-amplify/auth';
import axios, { AxiosError, HttpStatusCode, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';

/**
 * Axios Response Interceptor Configuration
 *
 * This interceptor handles authentication errors (401/403) globally across all API calls.
 * It implements a smart retry mechanism with token refresh before falling back to logout.
 *
 * Error Handling Strategy:
 * - 401 Unauthorized: Token has expired or is invalid → attempt token refresh → retry request
 * - 403 Forbidden: User lacks permissions → attempt token refresh → retry request
 * - Maximum 3 retry attempts with token refresh between each attempt
 * - If all retries fail → trigger logout
 *
 * Retry Flow:
 * 1. API call fails with 401/403
 * 2. Attempt to refresh token using fetchAuthSession({ forceRefresh: true })
 * 3. Update Axios Authorization header with new token
 * 4. Retry the original request with new token
 * 5. If retry fails with 401/403 again → repeat steps 2-4 (up to 3 times total)
 * 6. If retry succeeds → return response (transparent to caller)
 * 7. If all retries fail → logout user
 *
 * Integration with Silent Token Refresh:
 * - Silent refresh runs every 3 minutes in the background (AuthProvider)
 * - This interceptor provides reactive recovery when silent refresh misses an expiration
 * - Both mechanisms work together: refresh prevents errors, interceptor recovers from them
 *
 * Race Condition Handling:
 * - Uses flags to prevent multiple simultaneous token refreshes
 * - Queues concurrent 401/403 requests to wait for ongoing refresh
 * - Prevents duplicate logout calls
 */

const MAX_RETRY_ATTEMPTS = 3;

let isRefreshing = false;
let isLoggingOut = false;
let logoutCallback: (() => Promise<void>) | null = null;

// Queue to hold requests waiting for token refresh
interface PendingRequest {
    resolve: () => void;
    reject: (error: any) => void;
}
let failedRequestsQueue: PendingRequest[] = [];

/**
 * Processes the queue of failed requests after token refresh completes
 * @param error - If present, rejects all queued requests
 */
const processQueue = (error: any = null) => {
    failedRequestsQueue.forEach((promise) => {
        if (error) {
            promise.reject(error);
        } else {
            // No need to pass token - refreshTokens() already updated axios.defaults
            promise.resolve();
        }
    });
    failedRequestsQueue = [];
};

/**
 * Attempts to refresh the JWT tokens using AWS Amplify
 * @returns Promise resolving to the new tokens
 * @throws Error if token refresh fails
 */
export const refreshTokens = async (forceRefresh: boolean = false): Promise<AuthTokens> => {
    console.log('Attempting to refresh JWT tokens...');

    try {
        const session = await fetchAuthSession({ forceRefresh });
        const newJWTTTokens = session.tokens;
        if (!newJWTTTokens) {
            throw new Error('Failed to obtain new token');
        }

        // Update the default Axios Authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${newJWTTTokens.accessToken.toString()}`;

        console.log('Token refresh successful');
        return newJWTTTokens;
    } catch (error) {
        console.error('Token refresh failed:', error);
        throw error;
    }
};

/**
 * Handles authentication errors (401/403) with retry logic and token refresh
 * @param error - The Axios error object
 * @returns Promise resolving to the response or rejecting with error
 */
const handleAuthError = async (error: AxiosError): Promise<any> => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retryCount?: number };
    const status = error.response?.status;

    // Initialize retry count if not present
    if (!originalRequest._retryCount) {
        originalRequest._retryCount = 0;
    }

    if (isRetryConditionMet(originalRequest, status)) {
        const attemptNumber = originalRequest._retryCount + 1;
        console.warn(`[Axios Interceptor] Detected ${status} error.
            Attempting token refresh and retry (attempt ${attemptNumber}/${MAX_RETRY_ATTEMPTS}).`
        );

        // If a refresh is already in progress, queue this request
        if (isRefreshing) {
            console.log('[Axios Interceptor] Token refresh in progress, queuing request...');

            return new Promise((resolve, reject) => {
                failedRequestsQueue.push({
                    resolve: () => {
                        resolve(axios(originalRequest));
                    },
                    reject: (err: any) => {
                        reject(err);
                    },
                });
            });
        }

        // Increment retry count
        originalRequest._retryCount = attemptNumber;
        isRefreshing = true;

        try {
            // Attempt to refresh the token
            const newTokens = await refreshTokens(true); // force token refresh from Cognito for auth errrors.

            // Process any queued requests with the new token
            processQueue(null);

            // Retry the original request with new token
            console.log(`[Axios Interceptor] Retrying original request with new token (attempt ${attemptNumber}/${MAX_RETRY_ATTEMPTS})`);

            return axios(originalRequest);

        } catch (refreshError) {
            console.error('[Axios Interceptor] Token refresh failed, initiating logout');

            // Reject all queued requests
            processQueue(refreshError);

            // Trigger logout
            if (!isLoggingOut && logoutCallback) {
                isLoggingOut = true;

                try {
                    await logoutCallback();
                } catch (logoutError) {
                    console.error('[Axios Interceptor] Logout failed:', logoutError);
                } finally {
                    isLoggingOut = false;
                }
            }

            return Promise.reject(refreshError);

        } finally {
            isRefreshing = false;
        }
    }

    // If max retries exceeded, log and logout
    if ((status === 401 || status === 403) && originalRequest && originalRequest._retryCount >= MAX_RETRY_ATTEMPTS) {
        console.error(`[Axios Interceptor] Max retry attempts (${MAX_RETRY_ATTEMPTS}) reached. Logging out.`);

        if (!isLoggingOut && logoutCallback) {
            isLoggingOut = true;

            try {
                await logoutCallback();
            } catch (logoutError) {
                console.error('[Axios Interceptor] Logout failed:', logoutError);
            } finally {
                isLoggingOut = false;
            }
        }
    }

    // For other errors or retries that still fail, reject the promise
    return Promise.reject(error);
};

/**
 * Verify if retry conditions are met:
 * - 401/403
 * - 400 for AWS Cognito endpoint error, specifically
 *   "UnexpectedLambdaException: PreTokenGeneration invocation failed"
 * - and under max retries
 * @returns boolean when retry conditions are satisfied
 */
const isRetryConditionMet = (
    originalRequest: InternalAxiosRequestConfig & { _retryCount?: number },
    reqStatus: number | undefined
): boolean => {
    const AWS_COGNITO_IDP_ENDPOINT = "https://cognito-idp.ca-central-1.amazonaws.com/"
    console.log(`baseURL: ${originalRequest.baseURL}`);
    const retryCount = originalRequest._retryCount ?? 0;
    return (
        reqStatus === HttpStatusCode.Unauthorized // 401
        || reqStatus === HttpStatusCode.Forbidden // 403
        || (reqStatus === HttpStatusCode.BadRequest && originalRequest.baseURL === AWS_COGNITO_IDP_ENDPOINT)
    ) && originalRequest && retryCount < MAX_RETRY_ATTEMPTS;
}

/**
 * Initializes the Axios response interceptor.
 * Should be called once during app initialization (in AuthProvider onMounted).
 *
 * @param logout - Callback function to execute when recovery fails
 *                 This should be the logout function from AuthProvider
 */
export const setupAxiosInterceptor = (logout: () => Promise<void>) => {
    logoutCallback = logout;

    // Response interceptor
    axios.interceptors.response.use(
        // Success handler - pass through successful responses
        (response: AxiosResponse) => response,

        // Error handler - delegate to handleAuthError
        handleAuthError
    );

    console.log('[Axios Response Interceptor] configured successfully');
};

/**
 * Removes the axios interceptor (useful for cleanup or testing).
 */
export const removeAxiosInterceptor = () => {
    // Clear state
    logoutCallback = null;
    isLoggingOut = false;
    isRefreshing = false;
    failedRequestsQueue = [];

    console.log('[Axios Interceptor] Response interceptor removed');
};
