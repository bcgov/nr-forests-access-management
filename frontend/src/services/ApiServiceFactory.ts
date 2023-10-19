import httpInstance from '@/services/http/HttpCommon';
import {
    FAMApplicationsApi,
    FAMUserRoleAssignmentApi,
    FAMForestClientsApi,
    IDIRBCeIDProxyApi,
} from 'fam-api';

export class ApiServiceFactory {
    private applicationsApi: FAMApplicationsApi;
    private userRoleAssignmentApi: FAMUserRoleAssignmentApi;
    private forestClientApi: FAMForestClientsApi;
    private idirBceidProxyApi: IDIRBCeIDProxyApi;

    constructor() {
        // Instanciation for generated 'fam-api' client.
        this.applicationsApi = new FAMApplicationsApi(
            undefined,
            '',
            httpInstance
        ); // Note, Axios is strange, second parameter needs empty string, not null.
        this.userRoleAssignmentApi = new FAMUserRoleAssignmentApi(
            undefined,
            '',
            httpInstance
        );
        this.forestClientApi = new FAMForestClientsApi(
            undefined,
            '',
            httpInstance
        );
        this.idirBceidProxyApi = new IDIRBCeIDProxyApi(
            undefined,
            '',
            httpInstance
        );
    }

    getApplicationApi(): FAMApplicationsApi {
        return this.applicationsApi;
    }

    getUserRoleAssignmentApi(): FAMUserRoleAssignmentApi {
        return this.userRoleAssignmentApi;
    }

    getForestClientApi(): FAMForestClientsApi {
        return this.forestClientApi;
    }

    getIdirBceidProxyApi(): IDIRBCeIDProxyApi {
        return this.idirBceidProxyApi;
    }
}
