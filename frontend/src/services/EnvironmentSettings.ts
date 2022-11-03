export class EnvironmentSettings {

    getApiBaseUrl(): string {
        const apiBaseUrl = window.localStorage.getItem('fam_api_base_url') as string;
        return apiBaseUrl
    }

    getEnvironmentDisplayName(prefix = "", suffix=""): string {
        const environmentDisplayName = window.localStorage.getItem('environment_display_name') as string;
        if (environmentDisplayName.length == 0) {
            // For production we don't want to display anything for the environment so leave the display name blank.
            return environmentDisplayName
        } else {
            return prefix + environmentDisplayName + suffix
        }
    }

}