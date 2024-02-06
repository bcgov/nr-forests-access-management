import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import httpInstance from '@/services/http/HttpCommon';
import type { AxiosInstance } from 'axios';
import {
    AdminUserAccessesApi,
    FAMAccessControlPrivilegesApi,
    FAMApplicationAdminApi,
    FAMApplicationsApi
} from 'fam-admin-mgmt-api/api';
import {
    Configuration,
    FAMApplicationsApi as FAMAppsApi, // give alias so name does not clash with fam-admin-mgmt-api's FAMApplicationsApi
    FAMForestClientsApi,
    FAMUserRoleAssignmentApi,
    IDIRBCeIDProxyApi,
} from 'fam-app-acsctl-api';

type AppAccessControlApiType = {
    applicationsApi: FAMAppsApi;
    userRoleAssignmentApi: FAMUserRoleAssignmentApi;
    forestClientsApi: FAMForestClientsApi;
    idirBceidProxyApi: IDIRBCeIDProxyApi;
};

type AdminManagementApiType = {
    applicationAdminApi: FAMApplicationAdminApi;
    applicationsApi: FAMApplicationsApi;
    delegatedAdminApi: FAMAccessControlPrivilegesApi;
    adminUserAccessesApi: AdminUserAccessesApi;
};

export default class ApiServiceFactory {
    private static instance: ApiServiceFactory;

    private environmentSettings: EnvironmentSettings;
    private appAccessControlApiService: AppAccessControlApiType;
    private adminManagementApiService: AdminManagementApiType;

    /*
    Note, this class is a singleton; so the constructor is private.
    */
    private constructor() {
        this.environmentSettings = new EnvironmentSettings();
        const appAccessControlBaseURL =
            this.environmentSettings.getAppAcsctlApiBaseUrl();
        const adminManagementBaseURL =
            this.environmentSettings.getAdminMgmtApiBaseUrl();

        // App Access Control API service
        this.appAccessControlApiService = {
            applicationsApi: this.createApiInstance(
                FAMAppsApi,
                appAccessControlBaseURL
            ),
            userRoleAssignmentApi: this.createApiInstance(
                FAMUserRoleAssignmentApi,
                appAccessControlBaseURL
            ),
            forestClientsApi: this.createApiInstance(
                FAMForestClientsApi,
                appAccessControlBaseURL
            ),
            idirBceidProxyApi: this.createApiInstance(
                IDIRBCeIDProxyApi,
                appAccessControlBaseURL
            ),
        };

        this.adminManagementApiService = {
            applicationAdminApi: this.createApiInstance(
                FAMApplicationAdminApi,
                adminManagementBaseURL
            ),
            applicationsApi: this.createApiInstance(
                FAMApplicationsApi,
                adminManagementBaseURL
            ),
            delegatedAdminApi: this.createApiInstance(
                FAMAccessControlPrivilegesApi,
                adminManagementBaseURL
            ),
            adminUserAccessesApi: this.createApiInstance(
                AdminUserAccessesApi,
                adminManagementBaseURL
            )
        };
    }

    public static getInstance(): ApiServiceFactory {
        if (!ApiServiceFactory.instance) {
            ApiServiceFactory.instance = new ApiServiceFactory();
        }
        return ApiServiceFactory.instance;
    }

    getAppAccessControlApiService() {
        return this.appAccessControlApiService;
    }

    getAdminManagementApiService() {
        return this.adminManagementApiService;
    }

    /**
     * 'private' method using Typescript Generics, to instantiate Axios API(s) for this service provider.
     * @param c required class Types, the intended API 'class' to be instantiated.
     * @param baseURL optional, API's base URL (domain, and path if required).
     *                Will be set to `configuration` if baseURL is passed in.
     *                Note, for now, only the `baseURL` is the intended option. Also see
     *                `why` baseURL is set here at comment from @HttpCommon:defaultAxiosConfig.
     * @returns API class instantiated.
     */
    private createApiInstance<C>(
        // Class Types in Generics: see Typscript ref - https://www.typescriptlang.org/docs/handbook/2/generics.html
        // Obey the constructor signiture of the BaseAPI.
        c: new (
            configuration?: Configuration,
            basePath?: string,
            axios?: AxiosInstance
        ) => C,
        baseURL?: string
    ): C {
        const configuration = baseURL
            ? ({ baseOptions: { baseURL } } as Configuration)
            : undefined;
        return new c(configuration, '', httpInstance);
    }
}

export const apiServiceProvider = ApiServiceFactory.getInstance();
export const AdminMgmtApiService =
    apiServiceProvider.getAdminManagementApiService();
export const AppActlApiService =
    apiServiceProvider.getAppAccessControlApiService();
