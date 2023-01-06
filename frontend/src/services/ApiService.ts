import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import httpInstance from '@/services/http/HttpCommon';
import {
    FAMApplicationsApi,
    FAMRolesApi,
    FAMUserRoleAssignmentApi,
    FAMUsersApi
} from 'fam-api';

export enum ApiServiceName {
    ApplicationsApi = "ApplicationsApi",
    RolesApi = "RolesApi",
    UsersApi = "UsersApi",
    UserRoleAssignmentApi = "UserRoleAssignmentApi",
}

export class ApiService {
    // No trailing slash
    private apiUrl:string

    private applicationsApi: FAMApplicationsApi
    private rolesApi: FAMRolesApi
    private usersApi: FAMUsersApi
    private userRoleAssignmentApi: FAMUserRoleAssignmentApi

   constructor() {
       const environmentSettings = new EnvironmentSettings()
       this.apiUrl = environmentSettings.getApiBaseUrl()

       // Instanciation for generated 'fam-api' client.
       this.applicationsApi = new FAMApplicationsApi(null, '', httpInstance) // Note, Axios is strange, second parameter needs empty string, not null.
       this.rolesApi = new FAMRolesApi(null, '', httpInstance)
       this.usersApi = new FAMUsersApi(null, '', httpInstance)
       this.userRoleAssignmentApi = new FAMUserRoleAssignmentApi(null, '', httpInstance)
   }

   getApiService(serviceName: ApiServiceName): FAMApplicationsApi | FAMRolesApi | FAMUsersApi | FAMUserRoleAssignmentApi {
        switch(serviceName) {
            case ApiServiceName.ApplicationsApi:
                return this.applicationsApi
            case ApiServiceName.RolesApi:
                return this.rolesApi
            case ApiServiceName.UsersApi:
                return this.usersApi
            case ApiServiceName.UserRoleAssignmentApi:
                return this.userRoleAssignmentApi
            default:
                throw new Error(`${serviceName} service is not supported!`)
        }
   }

}