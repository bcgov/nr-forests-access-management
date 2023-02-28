import httpInstance from '@/services/http/HttpCommon';
import {
    FAMApplicationsApi,
    FAMRolesApi,
    FAMUserRoleAssignmentApi,
    FAMUsersApi,
} from 'fam-api';

export class ApiServiceFactory {
    private applicationsApi: FAMApplicationsApi;
    private rolesApi: FAMRolesApi;
    private userRoleAssignmentApi: FAMUserRoleAssignmentApi;
    private usersApi: FAMUsersApi;

    constructor() {
        // Instanciation for generated 'fam-api' client.
        this.applicationsApi = new FAMApplicationsApi(
            undefined,
            '',
            httpInstance
        ); // Note, Axios is strange, second parameter needs empty string, not null.
        this.rolesApi = new FAMRolesApi(undefined, '', httpInstance);
        this.userRoleAssignmentApi = new FAMUserRoleAssignmentApi(
            undefined,
            '',
            httpInstance
        );
        this.usersApi = new FAMUsersApi(undefined, '', httpInstance);
    }

    getApplicationApi(): FAMApplicationsApi {
        return this.applicationsApi;
    }

    getRolesApi(): FAMRolesApi {
        return this.rolesApi;
    }

    getUserRoleAssignmentApi(): FAMUserRoleAssignmentApi {
        return this.userRoleAssignmentApi;
    }

    getUsersApi(): FAMUsersApi {
        return this.usersApi;
    }
}
