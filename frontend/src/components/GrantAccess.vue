<script setup lang="ts">
import { selectedApplication, selectedApplicationDisplayText } from '@/services/ApplicationState'
import Breadcrumb from '@/components/Breadcrumb.vue'

</script>

<template>
  <div>

    <Breadcrumb activePage='Grant'/>

    <h1>Grant Access - {{selectedApplicationDisplayText}}</h1>

    <p>Selection: {{selectedApplication}}</p>

    <br/>TODO<br/>
  </div>
</template>

<style scoped>

</style>
