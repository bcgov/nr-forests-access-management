<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { selectedApplication, isApplicationSelected } from '../services/ApplicationService'

function selectedApplicationDisplayText() {
  if (selectedApplication.value) {  
    return `${selectedApplication.value.application_name.toUpperCase()}`
  }
  else {
    return ""
  }
}

</script>

<template>
  <div>
    
  <span><RouterLink to="/">Home</RouterLink> 
    &rarr; <RouterLink to="/application">Select Application</RouterLink> 
    &rarr; <RouterLink to="/manage">Manage Access {{selectedApplicationDisplayText()}}</RouterLink>
  </span>

  <h1>Manage Access {{selectedApplicationDisplayText()}}</h1>
  
  </div>
</template>

<style scoped>

</style>
