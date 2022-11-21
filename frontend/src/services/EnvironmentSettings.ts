export class EnvironmentSettings {

    env: any

    constructor() {
        this.env = JSON.parse(window.localStorage.getItem('env_data') as string)
        const environment = this.env?.env as string
        if (environment && (environment == 'dev' || environment == 'test')) {
            this.setEnvironmentDisplayName(environment)
        }
        else {
            this.setEnvironmentDisplayName('') // environment == 'prod'
        }
    }

    getApiBaseUrl(): string {
        let apiBaseUrl = this.env?.VUE_APP_API_GW_BASE_URL.value;
        apiBaseUrl? null : apiBaseUrl = 'http://127.0.0.1:8000' // local api
        return apiBaseUrl
    }

    getEnvironmentDisplayName(prefix = "", suffix=""): string {
        const environmentDisplayName = window.localStorage.getItem(this.environmentDisplayNameKey) as string;
        if (environmentDisplayName.length == 0) {
            // For production we don't want to display anything for the environment so leave the display name blank.
            return environmentDisplayName
        } else {
            return prefix + environmentDisplayName + suffix
        }
    }

    setEnvironmentDisplayName(name:string) {
        window.localStorage.setItem(this.environmentDisplayNameKey, name)
    }

    private environmentDisplayNameKey:string = 'fam_environment_display_name'
}