<script setup lang="ts">
import router from '@/router'
import { inject } from 'vue'
import { applicationsUserAdministers, selectedApplication, isApplicationSelected } from '../services/ApplicationService'
import type { Application } from '../services/ApplicationService'

// Need to inject during setup, not in timeout
const baseUrl = inject('fam_api_base_url')

// Using timeout to implement lazy loading. Component will render and display loading message until this finishes.
setTimeout( async () => {
  // Reload list each time we navigate to this page to avoid forcing user to refresh if their access changes.
  try {
    const url = baseUrl + '/api/v1/fam_applications'
    // TODO: Clean up logs and/or use logging solution?
    console.log(`Retrieving applications from ${url}`)
    const res = await fetch(`${url}`)
    var apps = await res.json()
    console.log(`Retrieved ${apps.length} applications`)
    console.log(apps)
    applicationsUserAdministers.value = apps as Application[]

  } catch (error) {
    // TODO: Better error handling.
    alert('Error retrieving applications from API, using fake test data... Error: ' + error)

    // TODO: Workaround broken front-end. Remove once front-end is stable.
    applicationsUserAdministers.value = [
      { application_name: 'FOM', application_description: 'Forest Operations Map', application_id: 1001 }, 
      { application_name: 'FAM', application_description: 'Forest Access Management', application_id: 1002 },
      { application_name: 'FAKE', application_description: 'Fake Test App', application_id: 9999 }
    ] as Application[]

  }

  // If can only manage one application redirect to manage access screen
  if (applicationsUserAdministers.value.length == 1) {
    selectedApplication.value = applicationsUserAdministers.value[0]
    router.push("/manage")
  }

})

</script>

<template>
  <div>

  <Breadcrumb activePage='SelectApp'/>

  <h1>Select Application</h1>

  <div v-if="applicationsUserAdministers.length">
    <label>Select the application to administer</label>
    <br/>
    <select v-model="selectedApplication" :size="applicationsUserAdministers.length+1">
      <option v-for="app in applicationsUserAdministers" :value="app">{{app.application_description}}</option>
    </select>
    <br/>
    <button @click="router.push('/manage')" :disabled="isApplicationSelected">Manage Access</button>
    &nbsp;
    <button @click="router.push('/grant')" :disabled="isApplicationSelected">Grant Access</button>
    <br/>
    <br/>
    <p>Selection: {{selectedApplication}}</p>
    <br/>
  </div>
  <div v-else>
    <p>Loading...</p>
  </div>
  </div>
</template>

