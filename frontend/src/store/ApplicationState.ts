import type { FamApplication } from 'fam-app-acsctl-api';
import { computed, ref } from 'vue';
import { FilterMatchMode } from 'primevue/api';

export const CURRENT_SELECTED_APPLICATION_KEY = 'CURRENT_SELECTED_APPLICATION';

// The applications the user has access to administer
export const applicationsUserAdministers = ref<FamApplication[]>([]);

// The application selected by the user to admin
export const selectedApplication = ref<FamApplication | null>(
    localStorage.getItem(CURRENT_SELECTED_APPLICATION_KEY)
        ? JSON.parse(
              localStorage.getItem(CURRENT_SELECTED_APPLICATION_KEY) as string
          )
        : null
);

// --- Setter

export const setApplicationsUserAdministers = (newValue: FamApplication[]) => {
    applicationsUserAdministers.value = newValue;
};

export const setSelectedApplication = (newValue: string | null) => {
    selectedApplication.value = JSON.parse(newValue as string);
    if (newValue)
        localStorage.setItem(CURRENT_SELECTED_APPLICATION_KEY, newValue);
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

export const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    'user.user_name': { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    'role.parent_role.role_name': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'role.role_name': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
    'role.client_number.forest_client_number': {
        value: null,
        matchMode: FilterMatchMode.CONTAINS,
    },
});