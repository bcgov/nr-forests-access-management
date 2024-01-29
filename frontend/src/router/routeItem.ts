export interface IRouteInfo {
    label: string;
    path: string;
    name: string;
}

export type RouteItems = {
    [key: string]: IRouteInfo;
};

export const routeItems = {
    landing: {
        name: 'landing',
        path: '/',
        label: 'Welcome to FAM',
    },
    dashboard: {
        name: 'dashboard',
        path: '/dashboard',
        label: 'Manage permissions',
    },
    grantUserPermission: {
        name: 'grantUserPermission',
        path: '/grant',
        label: 'Add user permission',
    },
    grantAppAdmin: {
        name: 'grantAppAdmin',
        path: '/grant-app-admin',
        label: 'Add application admin',
    },
} as RouteItems;