import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import httpInstance from '@/services/http/HttpCommon';
import type { AxiosInstance } from 'axios';
import {
    Configuration,
    FAMApplicationsApi,
    FAMForestClientsApi,
    FAMUserRoleAssignmentApi,
    IDIRBCeIDProxyApi
} from 'fam-app-acsctl-api';
import type { BaseAPI } from 'fam-app-acsctl-api/dist/base';

export class ApiServiceFactory {
    private environmentSettings: EnvironmentSettings;
    private applicationsApi: FAMApplicationsApi;
    private userRoleAssignmentApi: FAMUserRoleAssignmentApi;
    private forestClientApi: FAMForestClientsApi;
    private idirBceidProxyApi: IDIRBCeIDProxyApi;

    constructor() {
        this.environmentSettings = new EnvironmentSettings();
        const appAccessControlBaseURL = this.environmentSettings.getAppAcsctlApiBaseUrl();
        const adminManagementBaseURL = this.environmentSettings.getAdminMgmtApiBaseUrl();

        // App Access Control API service
        this.applicationsApi = this.createInstance(FAMApplicationsApi, appAccessControlBaseURL);
        this.userRoleAssignmentApi = this.createInstance(FAMUserRoleAssignmentApi, appAccessControlBaseURL);
        this.forestClientApi = this.createInstance(FAMForestClientsApi, appAccessControlBaseURL);
        this.idirBceidProxyApi = this.createInstance(IDIRBCeIDProxyApi, appAccessControlBaseURL);
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

    /**
     * This 'private' method is to instantiate Axios API(s) for the factory.
     * @param c required, the intended API class to be instantiated.
     * @param baseURL optional, API's base URL (domain, and path if required).
     *                Will be set to `configuration` if baseURL is passed in.
     *                Note, for now, only the `baseURL` is the intended option. Also see
     *                `why` baseURL is set here at comment from @HttpCommon:defaultAxiosConfig.
     * @returns API class instantiated.
     */
    private createInstance<C extends BaseAPI>(
        // Class Types in Generics: see Typscript ref - https://www.typescriptlang.org/docs/handbook/2/generics.html
        // Obey the constructor signiture of the BaseAPI.
        c: new (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) => C,
        baseURL?: string): C
    {
        const configuration = baseURL? {baseOptions: {baseURL}} as Configuration : undefined;
        return new c(
            configuration,
            '',
            httpInstance
        );
    }
}

