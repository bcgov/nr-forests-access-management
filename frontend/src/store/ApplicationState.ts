import { computed, ref } from 'vue';
import type { FamApplication } from 'fam-app-acsctl-api';
import { requireInjection } from '@/services/utils';
import ApiServiceFactory from '@/services/ApiServiceFactory';

export const CURRENT_SELECTED_APPLICATION_KEY = 'CURRENT_SELECTED_APPLICATION';

// The applications the user has access to administer
export const applicationsUserAdministers = ref<FamApplication[]>([]);

// The application selected by the user to admin
export const selectedApplication = ref<FamApplication | null>(
    localStorage.getItem(CURRENT_SELECTED_APPLICATION_KEY)
        ? JSON.parse(localStorage.getItem(CURRENT_SELECTED_APPLICATION_KEY) as string)
        : null
);

// --- Setter

export const setApplicationsUserAdministers = (newValue: FamApplication[]) => {
    applicationsUserAdministers.value = newValue;
}

export const setSelectedApplication = (newValue: string | null) => {
    selectedApplication.value = JSON.parse(newValue as string);
    if (newValue) localStorage.setItem(CURRENT_SELECTED_APPLICATION_KEY, newValue);
    else localStorage.removeItem(CURRENT_SELECTED_APPLICATION_KEY);
};

export const isApplicationSelected = computed(() => {
    return selectedApplication.value != undefined;
});

// --- Getter

export const selectedApplicationShortDisplayText = computed(() => {
    if (selectedApplication.value) {
        return `${selectedApplication.value.application_name.toUpperCase()}`;
    } else {
        return '';
    }
});

export const selectedApplicationDisplayText = computed(() => {
    if (selectedApplication.value) {
        return `${selectedApplication.value.application_description}`;
    } else {
        return '';
    }
});

// --- Fetching (backend)

export const fetchApplications = async () => {
    // TODO: find a way to refactor this "requireInjection" only for vue component and won't work properly here.
    const appActlApiService = requireInjection(ApiServiceFactory.APP_ACCESS_CONTROL_API_SERVICE_KEY);
    const fetchedData = (await appActlApiService.applicationsApi.getApplications()).data;
    setApplicationsUserAdministers(fetchedData);
};
