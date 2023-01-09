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

export class ApiServiceFactory {
    private applicationsApi: FAMApplicationsApi
    private rolesApi: FAMRolesApi
    private usersApi: FAMUsersApi
    private userRoleAssignmentApi: FAMUserRoleAssignmentApi

   constructor() {
       // Instanciation for generated 'fam-api' client.
       this.applicationsApi = new FAMApplicationsApi(undefined, '', httpInstance) // Note, Axios is strange, second parameter needs empty string, not null.
       this.rolesApi = new FAMRolesApi(undefined, '', httpInstance)
       this.usersApi = new FAMUsersApi(undefined, '', httpInstance)
       this.userRoleAssignmentApi = new FAMUserRoleAssignmentApi(undefined, '', httpInstance)
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