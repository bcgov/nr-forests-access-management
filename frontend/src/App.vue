<!-- <script setup lang="ts"> -->
<script lang="ts">
  import { RouterLink, RouterView } from 'vue-router'
  import Header from '@/components/Header.vue'
  import Footer from '@/components/Footer.vue'

  export default {
    components: {
      FamHeader: Header,
      FamFooter: Footer
    }
  }

</script>

<template>
  <FamHeader />

  <main class="p-0 mt-4">
    <RouterView />
  </main>

  <FamFooter />

</template>

<style scoped>
</style>
