<script setup lang="ts">
import router from '@/router';
import { selectedApplication, isApplicationSelected, selectedApplicationDisplayText } from '../services/ApplicationService'
import Breadcrumb from './Breadcrumb.vue'

var foo = 2;
</script>

<template>
  <div>
  <Breadcrumb activePage='Manage'/>

  <h1>Manage Access - {{selectedApplicationDisplayText}}</h1>

  <button @click="router.push('/grant')" :disabled="isApplicationSelected">Grant Access</button>

  <p>Selection: {{selectedApplication}}</p>
  <br/>TODO<br/>
  </div>
</template>

<style scoped>

</style>
