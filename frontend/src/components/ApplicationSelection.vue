<script setup lang="ts">
import { ref } from 'vue'

const selected = ref(null)
// TODO: Change to javascript object with id, name, description for each application.
const applications = ['Forest Operations Map (FOM)', 'Forest Access Management (FAM)', 'Forest Operations Plan (FOP)']

function manage(event: Event) {
  alert(`Manage app ${selected.value}`)
  // alert(event.target.tagName)
}
</script>

<template>
  <div v-if="applications.length">
  <label>Application to Administer</label>
  <br/>
  <select v-model="selected" :size="applications.length+1" >
    <!--<option disabled value="">Please select one</option> -->
    <option v-for="app in applications" :value="app">{{app}}</option>
  </select>
  <br />
  <p>Selected application: {{selected}}</p>
  <br/>
  <button @click="manage">Manage Access</button>
  &nbsp;
  <button>Grant Access</button>
  </div>
  <div v-else>
    <p>You are not authorized to administer any applications.</p>
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
