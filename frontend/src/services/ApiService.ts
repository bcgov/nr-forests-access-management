import type { Application } from '@/services/ApplicationState';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';

export class ApiService {

    private _apiUrl:string

    constructor() {
        const environmentSettings = new EnvironmentSettings()
        this._apiUrl = environmentSettings.getApiBaseUrl() + '/api/v1'
    }

    async getApplications():Promise<Application[]> {
        const url = this._apiUrl + '/fam_applications'
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
            console.log("Error retrieving applications via ${url}")
            throw error
        }
    }

}