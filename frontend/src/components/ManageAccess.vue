<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import router from '@/router';
import { isApplicationSelected, selectedApplication } from '@/services/ApplicationState';

var foo = 2;
</script>

<template>
  <div>
  
  <PageTitle />

  <button @click="router.push('/grant')" :disabled="isApplicationSelected">Grant Access</button>

  <p>Selection: {{selectedApplication}}</p>
  <br/>TODO<br/>
  </div>
</template>

<style scoped>

</style>
