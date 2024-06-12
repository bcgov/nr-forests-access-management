import type { FamApplicationDto } from 'fam-admin-mgmt-api/model';
import { computed, ref } from 'vue';

export const CURRENT_SELECTED_APPLICATION_KEY = 'CURRENT_SELECTED_APPLICATION';

export const selectedApplication = ref<FamApplicationDto | null>(
    localStorage.getItem(CURRENT_SELECTED_APPLICATION_KEY)
        ? JSON.parse(
            localStorage.getItem(CURRENT_SELECTED_APPLICATION_KEY) as string
        )
        : null
);

// --- Setter

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
    return selectedApplication.value?.id
})

// --- Getter

export const selectedApplicationShortDisplayText = computed(() => {
    if (selectedApplication.value) {
        return `${selectedApplication.value.name.toUpperCase()}`;
    } else {
        return '';
    }
});

export const selectedApplicationDisplayText = computed(() => {
    if (selectedApplication.value) {
        return `${selectedApplication.value.description}`;
    } else {
        return '';
    }
});
