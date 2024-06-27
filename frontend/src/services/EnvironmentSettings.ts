export class EnvironmentSettings {
    env: any;

    private environmentDisplayNameKey: string = 'fam_environment_display_name';

    private readonly API = {
        ADMIN_MANAGEMENT_API: 'admin_management_api',
        APP_ACCESS_CONTROL_API: 'app_access_control_api',
    };

    constructor() {
        this.env = JSON.parse(
            window.localStorage.getItem('env_data') as string
        );
        const environment = this.env?.target_env.value as string;
        if (
            environment &&
            (environment == 'dev' ||
                environment == 'test' ||
                environment == 'tools')
        ) {
            this.setEnvironmentDisplayName(environment);
        } else {
            this.setEnvironmentDisplayName(''); // environment == 'prod'
        }
    }

    getIdentityProviderIdir(): string {
        return this.env?.fam_console_idp_name.value;
    }

    getIdentityProviderBceid(): string {
        return this.env?.fam_console_idp_name_bceid.value;
    }

    // Admin Management API
    getAdminMgmtApiBaseUrl(): string {
        return this.getApiBaseUrl(this.API.ADMIN_MANAGEMENT_API);
    }

    // App Access Control API
    getAppAcsctlApiBaseUrl(): string {
        return this.getApiBaseUrl(this.API.APP_ACCESS_CONTROL_API);
    }

    getEnvironmentDisplayName(prefix = '', suffix = ''): string {
        const environmentDisplayName = window.localStorage.getItem(
            this.environmentDisplayNameKey
        ) as string;
        if (environmentDisplayName.length == 0) {
            // For production we don't want to display anything for the environment so leave the display name blank.
            return environmentDisplayName;
        } else {
            return prefix + environmentDisplayName + suffix;
        }
    }

    setEnvironmentDisplayName(name: string) {
        window.localStorage.setItem(this.environmentDisplayNameKey, name);
    }

    isDevEnvironment() {
        if (window.localStorage.getItem(this.environmentDisplayNameKey) == 'dev') {
            return true
        }
        return false
    }

    private getApiBaseUrl(useApi?: string) {
        let apiBaseUrl;

        // Default to 'ADMIN_MANAGEMENT_API'
        if (!useApi || useApi == this.API.ADMIN_MANAGEMENT_API) {
            apiBaseUrl =
                this.env?.fam_admin_management_api_base_url.value ||
                'http://localhost:8001'; // local api
        } else {
            apiBaseUrl =
                this.env?.fam_api_base_url.value || 'http://localhost:8000';
        }
        return apiBaseUrl;
    }
}
