<script setup lang="ts">
import { selectedApplicationDisplayText } from '../services/ApplicationService'
import Breadcrumb from './Breadcrumb.vue'

</script>

<template>
  <div>
    
    <Breadcrumb activePage='Grant'/>
    
    <h1>Grant Access - {{selectedApplicationDisplayText}}</h1>
  
    <br/>TODO<br/>
  </div>
</template>

<style scoped>

</style>
