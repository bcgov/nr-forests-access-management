<script setup lang="ts">
import { selectedApplication, isApplicationSelected, selectedApplicationDisplayText } from '../services/ApplicationService'
import Breadcrumb from './Breadcrumb.vue'

</script>

<template>
  <div>
    
    <Breadcrumb activePage='Grant'/>
  
  <h1>Grant Access - {{selectedApplicationDisplayText}}</h1>
  
  </div>
</template>

<style scoped>

</style>
