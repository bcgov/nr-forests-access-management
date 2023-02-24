<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import { ApiServiceFactory } from '@/services/ApiServiceFactory';
import {
    applicationsUserAdministers,
    isApplicationSelected,
    selectedApplication,
} from '@/services/ApplicationState';
import { onMounted } from 'vue';
import router from '../router';

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
            selectedApplication.value = applicationsUserAdministers.value[0];
            router.push('/manage');
        }
    } catch (error: any) {
        return Promise.reject(error);
    }
});
</script>

<template>
    <PageTitle :displaySelectedApplication="false"></PageTitle>

    <form id="selectApplicationForm" class="form-container">
        <div v-if="applicationsUserAdministers.length">
            <!-- Disabled - not needed for MVP -->
            <!-- Logic in script section:
        const environments = [
          "Prod", "Test", "Dev" // Dynamically assemble from list of apps.
        ]

        const environmentFilter = ref<string>("Prod")
        -->
            <!--
        <div class="row">
          <label>Filter by environment</label>
        </div>
        <div class="row">
          <div class="col-auto" v-for="env in environments">
            <input type="radio" id="r-env-{{env}}" name="envRadio" class="form-check-input" :value="env"
              v-model="environmentFilter" :checked="(environmentFilter === env)" />
              &nbsp;
            <label class="form-check-label" for="r-env-{{env}}">{{env}}</label>
          </div>
        </div>
        -->
            <div class="row">
                <div class="form-group col-md-5">
                    <label>Select the application to administer</label>

                    <select
                        id="applicationSelect"
                        class="form-select"
                        v-model="selectedApplication"
                        :size="applicationsUserAdministers.length + 1"
                    >
                        <option
                            v-for="app in applicationsUserAdministers"
                            :value="app"
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
