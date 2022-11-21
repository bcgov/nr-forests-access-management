export class EnvironmentSettings {

    readonly env = JSON.parse(window.localStorage.getItem('env_data') as string)

    getApiBaseUrl(): string {
        const apiBaseUrl = this.env.VUE_APP_API_GW_BASE_URL.value;
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