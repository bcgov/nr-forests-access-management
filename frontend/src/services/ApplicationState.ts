import type { FamApplication } from 'fam-api';
import { computed, ref } from 'vue';

// The applications the user has access to administer
export const applicationsUserAdministers = ref<FamApplication[]>([]);

// The application selected by the user to admin
export const selectedApplication = ref<FamApplication | null>(
    localStorage.getItem('CURRENT_SELECTED_APPLICATION')
        ? JSON.parse(
              localStorage.getItem('CURRENT_SELECTED_APPLICATION') as string
          )
        : null
);

export const setSelectedApplication = (newValue: string | null) => {
    selectedApplication.value = JSON.parse(newValue as string);
    if (newValue)
        localStorage.setItem('CURRENT_SELECTED_APPLICATION', newValue);
    else localStorage.removeItem('CURRENT_SELECTED_APPLICATION');
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
