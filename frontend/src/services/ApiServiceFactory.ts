import httpInstance from '@/services/http/HttpCommon';
import {
    FAMApplicationsApi,
    FAMRolesApi,
    FAMUserRoleAssignmentApi,
    FAMUsersApi,
    FAMForestClientsApi,
    IDIRBCeIDProxyApi
} from 'fam-api';

export class ApiServiceFactory {
    private applicationsApi: FAMApplicationsApi;
    private rolesApi: FAMRolesApi;
    private userRoleAssignmentApi: FAMUserRoleAssignmentApi;
    private usersApi: FAMUsersApi;
    private forestClientApi: FAMForestClientsApi;
    private idirBceidProxyApi: IDIRBCeIDProxyApi;

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
        this.forestClientApi = new FAMForestClientsApi(undefined, '', httpInstance);
        this.idirBceidProxyApi = new IDIRBCeIDProxyApi(undefined, '', httpInstance)
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

    getForestClientApi(): FAMForestClientsApi {
        return this.forestClientApi;
    }

    getIdirBceidProxyApi(): IDIRBCeIDProxyApi {
        return this.idirBceidProxyApi;
    }
}
