<script setup lang="ts">
import router from '@/router';
import { ref, computed, watch } from 'vue'
import { selectedApplication, isApplicationSelected } from '../services/ApplicationService'

const applications = ref([
  { application_name: 'FOM', application_description: 'Forest Operations Map', application_id: '1001' }, 
  { application_name: 'FAM', application_description: 'Forest Access Management', application_id: '1002' },
  { application_name: 'FOP', application_description: 'Forest Operations Plan', application_id: '1003' }
])

watch(selectedApplication, async (newSelection) => {
  try {
    console.log('Trying to retrieve applications')

    const res = await fetch('https://341ihp76l2.execute-api.ca-central-1.amazonaws.com/test/api/v1/fam_applications')

    // https://nn24zzbo40.execute-api.ca-central-1.amazonaws.com/junk/api/v1/fam_applications
    // https://341ihp76l2.execute-api.ca-central-1.amazonaws.com/prod/api/v1/fam_applications')
    // TODO: Error:  Access to fetch at 'https://341ihp76l2.execute-api.ca-central-1.amazonaws.com/prod/api/v1/fam_applications' from origin 'http://localhost:5173' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource. If an opaque response serves your needs, set the request's mode to 'no-cors' to fetch the resource with CORS disabled.
    console.log(res);
    var apps = await res.json()
    console.log(apps)
    applications.value = apps
  } catch (error) {
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
    
  <span><RouterLink to="/">Home</RouterLink> 
    &rarr; <RouterLink to="/application">Select Application</RouterLink> 
  </span>

  <h1>Select Application</h1>

  <div v-if="applications.length">
  <label>Select the application to administer</label>
  <br/>
  <select v-model="selectedApplication" :size="applications.length+1">
    <!--<option disabled value="">Please select one</option> -->
    <option v-for="app in applications" :value="app">{{app.application_description}}</option>
  </select>
  <br />
  <p>Application application: {{selectedApplication}}</p>
  <br/>
  <button @click="router.push('/manage')" :disabled="isApplicationSelected">Manage Access</button>
  &nbsp;
  <button @click="router.push('/grant')" :disabled="isApplicationSelected">Grant Access</button>
  </div>
  <div v-else>
    <p>You are not authorized to administer any applications.</p>
  </div>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
