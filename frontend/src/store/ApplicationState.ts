import type { FamApplicationDto } from 'fam-admin-mgmt-api/model';
import type { FamApplication } from 'fam-app-acsctl-api';
import { computed, ref } from 'vue';

export const CURRENT_SELECTED_APPLICATION_KEY = 'CURRENT_SELECTED_APPLICATION';

// The applications the user has access to administer
// export const applicationsUserAdministers = ref<FamApplication[]>([]);
export const applicationsUserAdministers = ref<FamApplicationDto[]|undefined>([]);

// The application selected by the user to admin
export const selectedApplication = ref<FamApplication | null>(
    localStorage.getItem(CURRENT_SELECTED_APPLICATION_KEY)
        ? JSON.parse(
            localStorage.getItem(CURRENT_SELECTED_APPLICATION_KEY) as string
        )
        : null
);

// --- Setter

// export const setApplicationsUserAdministers = (newValue: FamApplication[]) => {
//     applicationsUserAdministers.value = newValue;
// };
export const setApplicationsUserAdministers = (newValue: FamApplicationDto[] | undefined) => {
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

export const selectedApplicationId = computed(() => {
    return selectedApplication.value?.application_id
})

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