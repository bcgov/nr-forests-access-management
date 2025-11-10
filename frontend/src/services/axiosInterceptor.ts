import { fetchAuthSession } from 'aws-amplify/auth';
import axios, { AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';

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
    resolve: (token: string) => void;
    reject: (error: any) => void;
}
let failedRequestsQueue: PendingRequest[] = [];

/**
 * Processes the queue of failed requests after token refresh completes
 * @param error - If present, rejects all queued requests; otherwise resolves with new token
 * @param newToken - The refreshed access token to use for retrying requests
 */
const processQueue = (error: any = null, newToken: string | null = null) => {
    failedRequestsQueue.forEach((promise) => {
        if (error) {
            promise.reject(error);
        } else if (newToken) {
            promise.resolve(newToken);
        }
    });
    failedRequestsQueue = [];
};

/**
 * Attempts to refresh the access token using AWS Amplify
 * @returns Promise resolving to the new access token string
 * @throws Error if token refresh fails
 */
const refreshAccessToken = async (): Promise<string> => {
    console.log('[Axios Interceptor] Attempting to refresh access token...');

    try {
        const session = await fetchAuthSession({ forceRefresh: true });
        const accessToken = session.tokens?.accessToken;

        if (!accessToken) {
            throw new Error('Failed to obtain new access token');
        }

        const tokenString = accessToken.toString();

        // Update the default Axios Authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${tokenString}`;

        console.log('[Axios Interceptor] Token refresh successful');
        return tokenString;
    } catch (error) {
        console.error('[Axios Interceptor] Token refresh failed:', error);
        throw error;
    }
};

/**
 * Initializes the Axios response interceptor.
 * Should be called once during app initialization (in AuthProvider onMounted).
 *
 * @param onUnauthorized - Callback function to execute when recovery fails
 *                         This should be the logout function from AuthProvider
 */
export const setupAxiosInterceptor = (onUnauthorized: () => Promise<void>) => {
    logoutCallback = onUnauthorized;

    // Response interceptor
    axios.interceptors.response.use(
        // Success handler - pass through successful responses
        (response: AxiosResponse) => response,

        // Error handler - catch and process errors
        async (error: AxiosError) => {
            const originalRequest = error.config as InternalAxiosRequestConfig & { _retryCount?: number };
            const status = error.response?.status;

            // Initialize retry count if not present
            if (!originalRequest._retryCount) {
                originalRequest._retryCount = 0;
            }

            // Handle 401 Unauthorized and 403 Forbidden
            if ((status === 401 || status === 403) && originalRequest && originalRequest._retryCount < MAX_RETRY_ATTEMPTS) {
                const attemptNumber = originalRequest._retryCount + 1;
                console.warn(`[Axios Interceptor] Detected ${status} error. Attempting token refresh and retry (attempt ${attemptNumber}/${MAX_RETRY_ATTEMPTS}).`);

                // If a refresh is already in progress, queue this request
                if (isRefreshing) {
                    console.log('[Axios Interceptor] Token refresh in progress, queuing request...');

                    return new Promise((resolve, reject) => {
                        failedRequestsQueue.push({
                            resolve: (token: string) => {
                                originalRequest.headers['Authorization'] = `Bearer ${token}`;
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
                    const newToken = await refreshAccessToken();

                    // Process any queued requests with the new token
                    processQueue(null, newToken);

                    // Retry the original request with new token
                    originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
                    console.log(`[Axios Interceptor] Retrying original request with new token (attempt ${attemptNumber}/${MAX_RETRY_ATTEMPTS})`);

                    return axios(originalRequest);

                } catch (refreshError) {
                    console.error('[Axios Interceptor] Token refresh failed, initiating logout');

                    // Reject all queued requests
                    processQueue(refreshError, null);

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
        }
    );

    console.log('[Axios Interceptor] Response interceptor with retry logic configured successfully');
};

/**
 * Removes the axios interceptor (useful for cleanup or testing).
 * Resets all state variables to prevent memory leaks.
 */
export const removeAxiosInterceptor = () => {
    // Clear state
    logoutCallback = null;
    isLoggingOut = false;
    isRefreshing = false;
    failedRequestsQueue = [];

    console.log('[Axios Interceptor] Response interceptor removed');
};

/**
 * Request interceptor for logging (optional - currently disabled)
 * Useful for debugging but not critical for production
 */
export const setupRequestInterceptor = () => {
    axios.interceptors.request.use(
        (config: InternalAxiosRequestConfig) => {
            // Log outgoing requests in development
            if (import.meta.env.DEV) {
                console.debug(`[Axios] ${config.method?.toUpperCase()} ${config.url}`);
            }
            return config;
        },
        (error) => {
            console.error('[Axios Request] Error:', error);
            return Promise.reject(error);
        }
    );
};
