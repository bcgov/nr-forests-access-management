import { computed, ref } from 'vue';
import type { FamApplication } from 'fam-api';

// The applications the user has access to administer
export const applicationsUserAdministers = ref<FamApplication[]>([]);
export const currentSelectedApplication = 'CURRENT_SELECTED_APPLICATION';

// The application selected by the user to admin
export const selectedApplication = ref<FamApplication | null>(
    localStorage.getItem(currentSelectedApplication)
        ? JSON.parse(localStorage.getItem(currentSelectedApplication) as string)
        : null
);

export const setSelectedApplication = (newValue: string | null) => {
    selectedApplication.value = JSON.parse(newValue as string);
    if (newValue) localStorage.setItem(currentSelectedApplication, newValue);
    else localStorage.removeItem(currentSelectedApplication);
};

export const isApplicationSelected = computed(() => {
    return selectedApplication.value != undefined;
});

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
