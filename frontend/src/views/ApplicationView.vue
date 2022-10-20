
<script setup lang="ts">
import ApplicationSelection from '../components/ApplicationSelection.vue'
</script>

<template>
  <div>
    <h1>Choose Application</h1>
    <ApplicationSelection />
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
