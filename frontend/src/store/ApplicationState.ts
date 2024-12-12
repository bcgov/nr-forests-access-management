import { type FamApplicationGrantDto } from "fam-admin-mgmt-api/model";
import { ref } from "vue";

export const selectedApp = ref<FamApplicationGrantDto>();

// Optional: Helper function to update selectedApp
export const setSelectedApp = (app: FamApplicationGrantDto) => {
    selectedApp.value = app;
};

/**
 * The active tab index under a selected app
 */
export const activeTabIndex = ref(0);
