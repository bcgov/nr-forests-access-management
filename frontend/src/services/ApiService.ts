import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import type { Application } from '@/services/ApplicationState'

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
        try {
            // TODO: Clean up logs and/or use logging solution?
            console.log(`Retrieving applications from ${url}`)
            const res = await fetch(`${url}`)
            var apps = await res.json()
            console.log(`Retrieved ${apps.length} applications`)
            console.log(apps)
            return apps as Application[]
        } catch (error) {
            // TODO: Better error handling
            console.log(`Error retrieving applications via ${url}`)
            throw error
        }
    }

}