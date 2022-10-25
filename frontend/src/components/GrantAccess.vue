<script setup lang="ts">
import router from '@/router';
import { selectedApplication, isApplicationSelected, selectedApplicationDisplayText } from '../services/ApplicationService'

</script>

<template>
  <div>
    
  <span><RouterLink to="/">Home</RouterLink> 
    &rarr; <RouterLink to="/application">Select Application</RouterLink> 
    &rarr; <RouterLink to="/manage">Manage Access {{selectedApplicationDisplayText}}</RouterLink>
    &rarr; <RouterLink to="/grant">Grant Access {{selectedApplicationDisplayText}}</RouterLink>
  </span>

  <h1>Grant Access {{selectedApplicationDisplayText}}</h1>
  
  </div>
</template>

<style scoped>

</style>
