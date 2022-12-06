<script setup lang="ts">
import PageTitle from '@/components/PageTitle.vue';
import router from '@/router';
import { isApplicationSelected, selectedApplication } from '@/services/ApplicationState';
import { useToast } from 'vue-toastification';

var foo = 2;

function save(result: boolean) {
  const toast = useToast();
  if (result) {
    toast.success("Save successful")
  } else {
    toast.warning("Invalid selection.")
  }  
}

function saveError() {
  useToast().error("Save failed due to an error. Please try again. If the error persists then contact support.")
}

function uncaughtError() {
  throw new Error("test uncaught error thrown from function")
}

</script>

<template>
  <div>
  
  <PageTitle :displaySelectedApplication=true></PageTitle>

  <button @click="router.push('/grant')" :disabled="isApplicationSelected">Grant Access</button>

  <p>Selection: {{selectedApplication}}</p>
  <br/>TODO<br/>
  </div>
  &nbsp;
  <button @click="save(false)">Validation failure</button>
  &nbsp;
  <button @click="saveError()">Save Error</button>
  &nbsp;
  <button @click="uncaughtError()">Uncaught Error</button>
</template>

<style scoped>

</style>
