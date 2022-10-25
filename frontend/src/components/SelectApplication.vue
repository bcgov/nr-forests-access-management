<script setup lang="ts">
import router from '@/router';
import { ref, computed, watch } from 'vue'
import { selectedApplication, isApplicationSelected } from '../services/ApplicationService'
import type { Application } from '../services/ApplicationService'

// TODO: Maybe look into lazy loading via a timeout style function.

// Applications list is reset each time we navigate back to this page. We could cache this as shared state for the user session, 
// but safer and easier to just reload each time.
const applications = ref<Application[]>([])

// Use timeout to implement lazy loading. Component will render and display loading message until this finishes.
setTimeout( async () => {

if (applications.value.length == 0) {
  try {
    console.log('Trying to retrieve applications')
    // TODO: Parameterize URL
    const res = await fetch('https://341ihp76l2.execute-api.ca-central-1.amazonaws.com/test/api/v1/fam_applications')
    var apps = await res.json()
    console.log(`Retrieved ${apps.length} applications`)
    console.log(apps)
    applications.value = apps as Application[]
    // TODO: Redirect to error page or display error if no applications.
  } catch (error) {
    // TODO: Better error handling.
    alert('Error retrieving applications: ' + error)
  }
}
})
/*
const applications = ref([
  { application_name: 'FOM', application_description: 'Forest Operations Map', application_id: '1001' }, 
  { application_name: 'FAM', application_description: 'Forest Access Management', application_id: '1002' },
  { application_name: 'FOP', application_description: 'Forest Operations Plan', application_id: '1003' }
])

watch(selectedApplication, async (newSelection) => {
  try {
    console.log('Trying to retrieve applications')

    // TODO: Parameterize URL
    const res = await fetch('https://341ihp76l2.execute-api.ca-central-1.amazonaws.com/test/api/v1/fam_applications')

    // TODO: Invoke this after login
    console.log(res);
    var apps = await res.json()
    console.log(`Retrieved ${apps.length} applications`)
    console.log(apps)
    applications.value = apps
  } catch (error) {
    alert('Error retrieving applications: ' + error)
  }
})
*/
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
