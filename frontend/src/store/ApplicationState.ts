import { type FamApplicationDto } from "fam-admin-mgmt-api/model";
import { ref } from "vue";

export const selectedApp = ref<FamApplicationDto>();

// Optional: Helper function to update selectedApp
export const setSelectedApp = (app: FamApplicationDto) => {
    selectedApp.value = app;
};

export const activeIndex = ref(0);
