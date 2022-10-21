<script setup lang="ts">
import { ref, computed } from 'vue'


const selected = ref(null)

const applications = [
  { name: 'FOM', description: 'Forest Operations Map', id: '1001' }, 
  { name: 'FAM', description: 'Forest Access Management', id: '1002' },
  { name: 'FOP', description: 'Forest Operations Plan', id: '1003' }
]

const isActionsDisabled = computed( () => {
  return selected.value == null
})

function manage() {
  if (selected.value) {
    alert(`Manage app ${selected.value.description}`)
  } else {
    // Not really required, button is disabled if nothing is selected.
    alert('Please select an option');
  }
}
</script>

<template>
  <div v-if="applications.length">
  <label>Application to Administer</label>
  <br/>
  <select v-model="selected" :size="applications.length+1">
    <!--<option disabled value="">Please select one</option> -->
    <option v-for="app in applications" :value="app">{{app.description}}</option>
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
