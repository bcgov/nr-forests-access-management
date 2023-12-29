export interface IRouteInfo {
    label: string;
    path: string;
}

export type RouteItems = {
    [key: string]: IRouteInfo;
};

export const routeItems = {
    landing: {
        path: '/',
        label: 'Welcome to FAM',
    },
    dashboard: {
        path: '/dashboard',
        label: 'Manage permissions',
    },
    addUserPermission: {
        path: '/grant',
        label: 'Add user permission',
    },
} as RouteItems;