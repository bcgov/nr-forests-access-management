<!-- <script setup lang="ts"> -->
<script>
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

  <main>
    <RouterView />
  </main>

  <FamFooter />

</template>

<style scoped>
</style>
