import type { Application } from '@/services/ApplicationState';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import Http from '@/services/http/HttpCommon';

export class ApiService {

    // No trailing slash
    private apiUrl:string

    constructor() {
        const environmentSettings = new EnvironmentSettings()
        
        this.apiUrl = environmentSettings.getApiBaseUrl()
        // Allow for case when URL is specified without trailing slash
        if (!this.apiUrl.endsWith('/')) {
            this.apiUrl += '/'
        }
        this.apiUrl += 'api/v1'
    }

    async getApplications():Promise<Application[]> {
        const url = this.apiUrl + '/fam_applications'
        // TODO: Clean up logs and/or use logging solution?
        console.log(`Retrieving applications from ${url}`)
        const res = await Http.get(url);
        if (res == undefined) {
            throw new Error(`Failure retrieving applications from ${url}`)
        }
        const apps = res.data;
        return apps;
    }

    async getApplicationRoles(applicationId: number | undefined):Promise<ApplicationRoleResponse[] | null> {
        if (!applicationId) return null
        
        const url = this.apiUrl + `/fam_applications/${applicationId}/fam_roles`
        const res = await Http.get(url);
        if (res == undefined) {
            throw new Error(`Failure retrieving application roles from ${url}`)
        }
        const apps = res.data;
        return apps;
    }
}

export interface ApplicationRoleResponse {
    role_name: string,
    role_purpose: string,
    parent_role_id: number,
    application_id: number,
    forest_client_number: string,
    create_user: string,
    role_type_code: string,
    role_id: number
}