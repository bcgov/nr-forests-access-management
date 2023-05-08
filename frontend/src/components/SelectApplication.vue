<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import {
    applicationsUserAdministers,
    isApplicationSelected,
    selectedApplication,
    setSelectedApplication,
} from '@/services/ApplicationState';
import { onMounted, ref, computed } from 'vue';
import router from '../router';

const environments = ['All', 'Prod', 'Test', 'Dev']; // TODO: this could be dynamically loaded from the backend in the future

const environmentFilter = ref<string>(environments[0]); // Array item 0 is for the All options

const apiServiceFactory = new ApiServiceFactory();
const applicationsApi = apiServiceFactory.getApplicationApi();

onMounted(async () => {
    // Reload list each time we navigate to this page to avoid forcing user to refresh if their access changes.
    try {
        applicationsUserAdministers.value = (
            await applicationsApi.getApplications()
        ).data;
        // If user can only manage one application redirect to manage access screen
        if (applicationsUserAdministers.value.length == 1) {
            setSelectedApplication(
                JSON.stringify(applicationsUserAdministers.value[0])
            );
            router.push('/manage');
        }
    } catch (error: any) {
        return Promise.reject(error);
    }
});

const filterEnv = (selectedEnv: string) => {
    environmentFilter.value = selectedEnv;
    setSelectedApplication(null);
};

const filteredOptions = computed(() => {
    return environmentFilter.value === environments[0] // If the option is All, show everything. Otherwise, filter it
        ? applicationsUserAdministers.value
        : applicationsUserAdministers.value.filter((item) => {
              return item.app_environment?.includes(
                  environmentFilter.value.toUpperCase()
              );
          });
});

const selectApplication = (e: Event) => {
    setSelectedApplication(
        e.target ? (e.target as HTMLTextAreaElement).value : null
    );
};
</script>

<template>
    <PageTitle :displaySelectedApplication="false"></PageTitle>

    <form id="selectApplicationForm" class="form-container">
        <div v-if="applicationsUserAdministers.length">
            <div class="row">
                <label>Filter by environment</label>
            </div>
            <div class="row">
                <RadioGroup
                    :options="environments"
                    :initialValue="environmentFilter"
                    @change="filterEnv"
                ></RadioGroup>
            </div>
            <div class="row">
                <div class="form-group col-md-5">
                    <label>Select the application to administer</label>
                    <select
                        id="applicationSelect"
                        class="form-select"
                        :value="JSON.stringify(selectedApplication)"
                        @change="selectApplication"
                        :size="applicationsUserAdministers.length + 1"
                    >
                        <option
                            v-for="app in filteredOptions"
                            :value="JSON.stringify(app)"
                        >
                            {{ app.application_description }}
                        </option>
                    </select>
                </div>
            </div>
            <div class="row gy-3">
                <div class="col-auto">
                    <button
                        type="button"
                        id="goToManageAccessButton"
                        class="btn btn-info mb-3"
                        :disabled="!isApplicationSelected"
                        @click="router.push('/manage')"
                    >
                        Manage Access
                    </button>
                </div>
                <div class="col-auto">
                    <button
                        type="button"
                        id="goToGrantAccessButton"
                        class="btn btn-primary mb-3"
                        :disabled="!isApplicationSelected"
                        @click="router.push('/grant')"
                    >
                        Grant Access
                    </button>
                </div>
            </div>
        </div>

        <div v-else>
            <p>Loading applications...</p>
        </div>
    </form>
</template>

<style lang="scss" scoped>
@import '@/assets/styles/styles.scss';
</style>
