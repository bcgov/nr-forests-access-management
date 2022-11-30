<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import { ApiService } from '@/services/ApiService';
import type { Application } from '@/services/ApplicationState';
import { applicationsUserAdministers, isApplicationSelected, selectedApplication } from '@/services/ApplicationState';
import { useToast } from 'vue-toastification';
import router from '../router';

const apiService = new ApiService()

// Using timeout to implement lazy loading. Component will render and display loading message until this finishes.
setTimeout( async () => {
  // Reload list each time we navigate to this page to avoid forcing user to refresh if their access changes.
  try {
    applicationsUserAdministers.value = await apiService.getApplications()
  } catch (error) {
    const toast = useToast();
    toast.error("An error occurred loading applications. Please refresh the screen.\n If the error persists, try again later or contact support.")
    // TODO: Workaround broken front-end. Remove once front-end is stable.
    toast.warning("Using fake test data as temporary working for applications not working. REMOVE BEFORE PRODUCTION.")
    applicationsUserAdministers.value = [
      { application_name: 'FOM', application_description: 'Forest Operations Map', application_id: 1001 }, 
      { application_name: 'FAM', application_description: 'Forest Access Management', application_id: 1002 },
      { application_name: 'FAKE', application_description: 'Fake Test App', application_id: 9999 }
    ] as Application[]

  }

  // If user can only manage one application redirect to manage access screen
  if (applicationsUserAdministers.value.length == 1) {
    selectedApplication.value = applicationsUserAdministers.value[0]
    router.push("/manage")
  }

})

</script>

<template>
    <PageTitle :displaySelectedApplication=false></PageTitle>

    <form id="selectApplicationForm" class="form-container">
      <div v-if="applicationsUserAdministers.length">
        <div class="row">
          <div class="form-group col-md-5">
            <label>Select the application to administer</label>
            
            <select id="applicationSelect"
              class="form-select" 
              v-model="selectedApplication" 
              :size="applicationsUserAdministers.length+1">
              <option v-for="app in applicationsUserAdministers" :value="app">{{app.application_description}}</option>
            </select>
          </div>
        </div>
        <div class="row gy-3">
          <div class="col-auto">
            <button type="button"
              id="goToManageAccessButton" 
              class="btn btn-info mb-3"
              :disabled="isApplicationSelected"
              @click="router.push('/manage')">Manage Access</button>
          </div>
          <div class="col-auto">
            <button type="button"
              id="goToGrantAccessButton"
              class="btn btn-primary mb-3"
              :disabled="isApplicationSelected"
              @click="router.push('/grant')">Grant Access</button>
          </div>
        </div>

      </div>

      <div v-else>
        <p>Loading applications...</p>
      </div>
    </form>
</template>

<style lang="scss" scoped>
   @import "@/assets/styles/styles.scss";
</style>