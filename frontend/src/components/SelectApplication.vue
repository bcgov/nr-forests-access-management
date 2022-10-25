<script setup lang="ts">
import router from '@/router';
import { ref, inject } from 'vue'
import { selectedApplication, isApplicationSelected } from '../services/ApplicationService'
import type { Application } from '../services/ApplicationService'

// Applications list is reset each time we navigate back to this page. We could cache this as shared state for the user's session, 
// but safer and easier to just reload each time.
const applications = ref<Application[]>([])

// Need to inject during setup, not in timeout
const baseUrl = inject('fam_api_base_url')

// Use timeout to implement lazy loading. Component will render and display loading message until this finishes.
setTimeout( async () => {
  if (applications.value.length == 0) {
    try {
      // TODO: Clean up logs and/or use logging solution?
      const url = baseUrl + '/api/v1/fam_applications'
      console.log(`Retrieving applications from ${url}`)
      const res = await fetch(url)
      var apps = await res.json() as Application[]
      console.log(`Retrieved ${apps.length} applications`)
      console.log(apps)
      // apps = apps.slice(0,1) // To test only getting one application
      applications.value = apps
      // If only one application then select and redirect to Manage Access screen
      if (apps.length == 1) {
        // TODO: Update breadcrumb to not show Select Application screen?
        console.log('User has access to only one application - select and redirect to manage access screen.')
        selectedApplication.value = apps[0]
        router.push('/manage')
      }
      
      // TODO: Redirect to error page or display error if no applications.
    } catch (error) {
      // TODO: Better error handling.
      alert('Error retrieving applications: ' + error)
    }
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
    
  <span><RouterLink to="/">Home</RouterLink> 
    &rarr; <RouterLink to="/application">Select Application</RouterLink> 
  </span>

  <h1>Select Application</h1>

  <div v-if="applications.length">
    <label>Select the application to administer</label>
    <br/>
    <select v-model="selectedApplication" :size="applications.length+1">
      <option v-for="app in applications" :value="app">{{app.application_description}}</option>
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

<style scoped>

</style>
