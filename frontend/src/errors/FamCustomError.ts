// Custom FAM parent error.
export class FamCustomError extends Error {
    message: string;
    cause: Error | undefined; // Original error if any.
    constructor(message: string, cause?: Error) {
        super(message);
        this.message = message;
        this.cause = cause;
    }
}

// --- FamRouteError

export enum RouteErrorName {
    NOT_AUTHENTICATED_ERROR = 'NOT_AUTHENTICATED_ERROR',
    NO_APPLICATION_SELECTED_ERROR = 'NO_APPLICATION_SELECTED_ERROR',
    NO_ROLES_ERROR = 'NO_ROLES_ERROR'
}

type RouteInfo = { to: any, from: any };
/**
 * FAM custom route error.
 * For use only when needing to throw during router transition.
 */
export class FamRouteError extends FamCustomError {
    name: RouteErrorName;
    routeInfo: RouteInfo | undefined;

    constructor(name: RouteErrorName, message: string, routeInfo?: RouteInfo, cause?: Error) {
        super(message, cause);
        this.name = name;
        this.routeInfo = routeInfo;
    }
}