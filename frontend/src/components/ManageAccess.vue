<script setup lang="ts">
import router from '@/router';
import { selectedApplication, isApplicationSelected, selectedApplicationDisplayText } from '../services/ApplicationService'
import Breadcrumb from './Breadcrumb.vue'

</script>

<template>
  <div>
  <Breadcrumb activePage='Manage'/>

  <h1>Manage Access - {{selectedApplicationDisplayText}}</h1>

  <button @click="router.push('/grant')" :disabled="isApplicationSelected">Grant Access</button>
  
  </div>
</template>

<style scoped>

</style>
