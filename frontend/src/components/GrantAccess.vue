<script setup lang="ts">
import { selectedApplication, selectedApplicationDisplayText } from '@/services/ApplicationState'

</script>

<template>
  <div>
    
    <h1>Grant Access - {{selectedApplicationDisplayText}}</h1>
  
    <p>Selection: {{selectedApplication}}</p>

    <br/>TODO<br/>
  </div>
</template>

<style scoped>

</style>
