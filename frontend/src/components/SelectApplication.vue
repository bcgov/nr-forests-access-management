<script setup lang="ts">
import router from '@/router';
import { applicationsUserAdministers, selectedApplication, isApplicationSelected } from '../services/ApplicationService'
import type { Application } from '../services/ApplicationService'

// Using timeout to implement lazy loading. Component will render and display loading message until this finishes.
setTimeout( async () => {
  // Reload list each time we navigate to this page to avoid forcing user to refresh if their access changes.
  try {
    console.log('Trying to retrieve applications')
    const res = await fetch('https://341ihp76l2.execute-api.ca-central-1.amazonaws.com/test/api/v1/fam_applications')
    var apps = await res.json()
    console.log(`Retrieved ${apps.length} applications`)
    console.log(apps)
    applicationsUserAdministers.value = apps as Application[]
  } catch (error) {
    // TODO: Better error handling.
    alert('Error retrieving applications: ' + error)
  }

})

function manage() {
  if (selectedApplication.value) {   
    // alert(`Manage app ${selectedApplication.value.application_description}`)
    router.push('/manage')
  } else {
    // Not really required, button is disabled if nothing is selectedApplication.
    alert('Please select an option');
  }
}

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
    <p>You are not authorized to administer any applications.</p>
  </div>
  </div>
</template>

<style scoped>
</style>
