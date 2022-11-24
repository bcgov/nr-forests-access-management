<script setup lang="ts">
import { selectedApplication, selectedApplicationDisplayText } from '@/services/ApplicationState'

import { useToast } from 'vue-toastification'

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
    
    <h1>Grant Access - {{selectedApplicationDisplayText}}</h1>
  
    <p>Selection: {{selectedApplication}}</p>

    <br/>TODO<br/>
    <button @click="save(true)">Save</button>
    &nbsp;
    <button @click="save(false)">Validation failure</button>
    &nbsp;
    <button @click="saveError()">Save Error</button>
    &nbsp;
    <button @click="uncaughtError()">Uncaught Error</button>
  </div>
</template>

<style scoped>

</style>
