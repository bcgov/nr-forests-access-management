export interface IRouteInfo {
    label?: string;
    path: string;
    name: string;
}

export type RouteItems = {
    [key: string]: IRouteInfo;
};

export const routeItems: RouteItems = {
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
    managePermissions: {
        name: 'ManagePermissions',
        path: '/manage-permissions',
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
    grantDelegatedAdmin: {
        name: 'grantDelegatedAdmin',
        path: '/grant-delegated-admin',
        label: 'Add a delegated admin',
    },
    myPermissions: {
        name: 'myPermissions',
        path: '/my-permissions',
        label: 'Check my permissions',
    },
    userDetails: {
        name: 'viewUserDetails',
        path: '/user-details/users/:userName/user-type/:userTypeCode/applications/:applicationId',
        label: 'User details',
    },
};
