<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const selected = ref(null)

const applications = ref([
  { application_name: 'FOM', application_description: 'Forest Operations Map', application_id: '1001' }, 
  { application_name: 'FAM', application_description: 'Forest Access Management', application_id: '1002' },
  { application_name: 'FOP', application_description: 'Forest Operations Plan', application_id: '1003' }
])

watch(selected, async (newSelection) => {
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

const isActionsDisabled = computed( () => {
  return selected.value == null
})

function manage() {
  if (selected.value) {    
    alert(`Manage app ${selected.value.application_description}`)
  } else {
    // Not really required, button is disabled if nothing is selected.
    alert('Please select an option');
  }
}
</script>

<template>
  <div>
  <h1>Choose Application</h1>

  <div v-if="applications.length">
  <label>Application to Administer</label>
  <br/>
  <select v-model="selected" :size="applications.length+1">
    <!--<option disabled value="">Please select one</option> -->
    <option v-for="app in applications" :value="app">{{app.application_description}}</option>
  </select>
  <br />
  <p>Selected application: {{selected}}</p>
  <br/>
  <button @click="manage" :disabled="isActionsDisabled">Manage Access</button>
  &nbsp;
  <button :disabled="isActionsDisabled">Grant Access</button>
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
